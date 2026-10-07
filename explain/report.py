"""Pilot report: regret per cell, model-substitution comparisons, cost, samples.

Writes report.md, report.json and samples.md into the pilot workdir.
Regret is Stockfish win-rate regret in percentage points. A failed decision
(missing, refused, unparseable, illegal, empty) is scored as a uniformly random
legal move (its expected regret) and counted in fail%. Every cell also reports
regret over its successful decisions only, the share of one-ply children whose
reading failed, and the share of Queen reads whose prose was truncated.
"""

from __future__ import annotations

import json
import random
from collections import defaultdict
from statistics import mean

import chess

from datagen.self_distill.analysis import MOVE, field_map, pov_move
from explain.common import human, read_jsonl, render_heads

BOOT = 2000


def ci(values: list[float], seed: int = 0) -> tuple[float, float]:
    if len(values) < 2:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    means = sorted(mean(rng.choices(values, k=len(values))) for _ in range(BOOT))
    return means[int(0.025 * BOOT)], means[int(0.975 * BOOT)]


def label(row: dict) -> str:
    parts = [row["kind"], row["rung"], row["text"] or "-", row["agent"]]
    if not row["fen_shown"]:
        parts.append("noFEN")
    if row["effort"]:
        parts.append(f"effort={row['effort']}")
    return " | ".join(parts)


def cell_table(rows: list[dict]) -> list[dict]:
    groups = defaultdict(list)
    for row in rows:
        groups[label(row)].append(row)
    table = []
    for name, group in sorted(groups.items()):
        regrets = [100 * r["regret"] for r in group]
        ok = [100 * r["regret"] for r in group if not r["fallback_used"]]
        low, high = ci(regrets)
        children = sum(r.get("n_children", 0) for r in group)
        reads = sum(r.get("queen_reads", 0) for r in group)
        table.append({
            "cell": name, "n": len(group), "regret": mean(regrets), "ci": [low, high],
            "regret_ok": mean(ok) if ok else None,
            "fail_pct": 100 * mean(r["fallback_used"] for r in group),
            "child_fail_pct": (100 * sum(r.get("failed_children", 0) for r in group) / children
                               if children else None),
            "trunc_pct": (100 * sum(r.get("truncated_reads", 0) for r in group) / reads
                          if reads else None),
            "top1_pct": 100 * mean(r.get("move") == r["sf_best"] for r in group),
        })
    return table


def substitution(rows: list[dict], role: str, reference: str, swap) -> list[dict]:
    """Paired comparison of cells that differ only in one model slot.

    ``swap(row)`` returns (slot_model, key_without_slot) or None when the row
    has no such slot.
    """
    by_key = defaultdict(dict)
    for row in rows:
        slot = swap(row)
        if slot is None:
            continue
        model, key = slot
        by_key[(key, row["position_id"])][model] = row
    pairs = defaultdict(list)
    for (key, _), models in by_key.items():
        if reference not in models:
            continue
        for model, row in models.items():
            if model != reference:
                pairs[(model, key)].append((row, models[reference]))
    summary = defaultdict(list)
    out = []
    for (model, key), items in sorted(pairs.items(), key=lambda kv: str(kv[0])):
        diffs = [100 * (a["regret"] - b["regret"]) for a, b in items]
        agree = mean(a.get("move") == b.get("move") for a, b in items)
        summary[model].extend(diffs)
        out.append({"role": role, "model": model, "cell": key, "n": len(items),
                    "regret_diff": mean(diffs), "ci": ci(diffs), "move_agree_pct": 100 * agree})
    # Pooled row: average each position's differences across cells first, so the
    # bootstrap resamples positions (the independent unit), not cell-position pairs.
    for model in summary:
        by_position = defaultdict(list)
        for (m, _), items in pairs.items():
            if m == model:
                for a, b in items:
                    by_position[a["position_id"]].append(100 * (a["regret"] - b["regret"]))
        diffs = [mean(v) for v in by_position.values()]
        out.append({"role": role, "model": model, "cell": "ALL CELLS (per-position mean)",
                    "n": len(diffs), "regret_diff": mean(diffs), "ci": ci(diffs),
                    "move_agree_pct": None})
    return out


def agent_slot(row):
    if row["agent"] in ("hce", "mech", "queen"):
        return None
    return row["agent"], (row["kind"], row["rung"], row["text"], row["fen_shown"], row["effort"])


def writer_slot(row):
    text = row["text"] or ""
    if not text.startswith("h-"):
        return None
    writer, rest = text[2:].split("/", 1) if "/" in text else (text[2:], "")
    return writer, (row["kind"], row["rung"], rest, row["agent"], row["fen_shown"])


def consolidator_slot(row):
    text = row["text"] or ""
    parts = text.split("/")
    if len(parts) == 4 and parts[0] == "q" and parts[1] in ("d1", "rw"):
        return parts[2], (row["kind"], row["rung"], parts[1], parts[3], row["agent"], row["fen_shown"])
    return None


def costs(pilot) -> dict:
    by = defaultdict(lambda: {"calls": 0, "usd": 0.0, "tin": [], "tout": [], "errors": 0,
                              "refusals": 0})
    for row in pilot.llm.store.values():
        entry = by[(row["model"], row.get("tag", ""))]
        entry["calls"] += 1
        entry["usd"] += row.get("cost_usd", 0.0)
        entry["errors"] += bool(row.get("error"))
        entry["refusals"] += row.get("stop_reason") == "refusal"
        if not row.get("error"):
            entry["tin"].append(row["tokens_in"])
            entry["tout"].append(row["tokens_out"])
    out = {}
    for (model, tag), entry in sorted(by.items()):
        out[f"{model}/{tag}"] = {
            "calls": entry["calls"], "usd": entry["usd"], "errors": entry["errors"],
            "refusals": entry["refusals"],
            "usd_per_call": entry["usd"] / max(1, entry["calls"] - entry["errors"]),
            "mean_in": mean(entry["tin"]) if entry["tin"] else 0,
            "mean_out": mean(entry["tout"]) if entry["tout"] else 0,
        }
    return out


def gpu_stats(store) -> dict:
    rows = store.values()
    if not rows:
        return {}
    tokens = [r["output_tokens"] for r in rows]
    batches = {(r["batch_seconds"], r["batch_size"]): r["batch_seconds"] for r in rows}
    seconds = sum(batches.values())
    return {"requests": len(rows), "mean_output_tokens": mean(tokens),
            "p90_output_tokens": sorted(tokens)[int(0.9 * (len(tokens) - 1))],
            "generation_seconds": seconds,
            "requests_per_gpu_hour": len(rows) / (seconds / 3600) if seconds else None}


def compliance(pilot) -> dict:
    """Share of writer outputs Queen can read (vocabulary and field checks)."""
    counts = defaultdict(lambda: [0, 0])
    for position in pilot.positions:
        for text_id, text in pilot.root_texts(position).items():
            if text_id.startswith("q/d0") or text_id == "q/d1/minimax":
                continue
            writer = text_id.split("/")[2] if text_id.startswith("q/") else text_id.split("/")[0][2:]
            if text_id.startswith("h-") and "/d1/" in text_id:
                writer = "qwen"
            counts[writer][0] += text["ok"]
            counts[writer][1] += 1
        for texts in pilot.child_texts(position).values():
            for source, text in texts.items():
                if source.startswith("h-"):
                    counts[source[2:]][0] += text["ok"]
                    counts[source[2:]][1] += 1
    return {model: {"ok": ok, "total": total, "pct": 100 * ok / total}
            for model, (ok, total) in counts.items()}


def tree_sources(pilot) -> dict:
    """Why the shared tree's children are not always Queen's own candidates.

    For each root generation: whether BEST_MOVE parsed to a legal move, how many
    PROMISING_MOVES were written and how many were legal, how many distinct legal
    root moves the ANALYSIS mentions, and how many of the three children came
    from Queen (the rest are topped up by move_priority).
    """
    rows = []
    for position in pilot.positions:
        fen = position["fen"]
        generation = pilot.generation(fen)
        if generation is None:
            continue
        board = chess.Board(fen)
        fields = field_map(generation)

        def legal(section):
            moves = []
            for atom in MOVE.finditer(fields.get(section, "")):
                move, _ = pov_move(atom, board.copy(stack=False), board.turn)
                if move is not None and move not in moves:
                    moves.append(move)
            return moves

        written = len(MOVE.findall(fields.get("PROMISING_MOVES", "")))
        best, promising, analysis = legal("BEST_MOVE"), legal("PROMISING_MOVES"), legal("ANALYSIS")
        queen = len(dict.fromkeys(best + promising + analysis))
        rows.append({"best_legal": bool(best), "promising_written": written,
                     "promising_legal": len(promising), "analysis_moves": len(analysis),
                     "queen_children": min(3, queen)})
    if not rows:
        return {}
    n = len(rows)
    return {
        "positions": n,
        "queen_children_dist": {k: sum(r["queen_children"] == k for r in rows) for k in range(4)},
        "best_move_legal_pct": 100 * mean(r["best_legal"] for r in rows),
        "mean_promising_written": mean(r["promising_written"] for r in rows),
        "mean_promising_legal": mean(r["promising_legal"] for r in rows),
        "promising_illegal_pct": 100 * (1 - sum(r["promising_legal"] for r in rows)
                                        / max(1, sum(r["promising_written"] for r in rows))),
        "mean_analysis_moves": mean(r["analysis_moves"] for r in rows),
    }


def rates(rows: list[dict]) -> dict:
    """Overall failure, child-failure and truncation rates, by agent."""
    out = defaultdict(lambda: {"decisions": 0, "failed": 0, "children": 0,
                               "failed_children": 0, "reads": 0, "truncated": 0})
    for r in rows:
        e = out[r["agent"]]
        e["decisions"] += 1
        e["failed"] += r["fallback_used"]
        e["children"] += r.get("n_children", 0)
        e["failed_children"] += r.get("failed_children", 0)
        e["reads"] += r.get("queen_reads", 0)
        e["truncated"] += r.get("truncated_reads", 0)
    return dict(out)


def pct(a: int, b: int) -> str:
    return f"{100 * a / b:.1f}% ({a}/{b})" if b else "–"


def fmt_ci(pair) -> str:
    return f"[{pair[0]:+.2f}, {pair[1]:+.2f}]"


def write_samples(pilot, path, count: int = 10) -> None:
    rng = random.Random(1)
    positions = rng.sample(pilot.positions, min(count, len(pilot.positions)))
    decisions = defaultdict(list)
    for row in read_jsonl(pilot.dir / "decisions.jsonl"):
        decisions[row["position_id"]].append(row)
    lines = ["# Pilot samples for reading", ""]
    for position in positions:
        fen = position["fen"]
        texts = pilot.root_texts(position)
        lines += [f"## {position['position_id']}", f"FEN: `{fen}`", ""]
        for text_id in sorted(texts):
            text = texts[text_id]
            if text_id == "q/d1/minimax" or text_id.endswith("/full"):
                continue
            lines.append(f"### {text_id}")
            if not text["ok"]:
                lines += [f"FAILED: {text['error']}", "", "```", text.get("raw", "")[:1500], "```", ""]
                continue
            lines += [human(text["prose"], fen), ""]
            if text.get("heads"):
                lines += ["Heads:", "```", render_heads(fen, text["heads"]), "```", ""]
        lines.append("### Reasons given by readers and choosers")
        for row in decisions[position["position_id"]]:
            if row.get("reason") and row["kind"] in ("chooser", "depth") and row["fen_shown"]:
                lines.append(f"- {label(row)} -> {row.get('move')} "
                             f"(regret {100 * row['regret']:.1f}pp): {row['reason']}")
        lines.append("")
    path.write_text("\n".join(lines))


def write_report(pilot) -> None:
    rows = pilot.decisions()
    table = cell_table(rows)
    reference = pilot.judge
    comparisons = (substitution(rows, "reader/chooser", reference, agent_slot)
                   + substitution(rows, "hybrid writer", reference, writer_slot)
                   + substitution(rows, "consolidator", reference, consolidator_slot))
    report = {"cells": table, "substitution": comparisons, "costs": costs(pilot),
              "queen_gpu": gpu_stats(pilot.queen), "qwen_gpu": gpu_stats(pilot.qwen),
              "compliance": compliance(pilot), "api_spent_usd": pilot.llm.ledger.spent,
              "rates": rates(rows), "tree_sources": tree_sources(pilot)}
    (pilot.dir / "report.json").write_text(json.dumps(report, indent=2, default=list))

    lines = ["# Pilot report", "",
             f"Positions: {len(pilot.positions)}. API spend: ${pilot.llm.ledger.spent:.2f}. "
             "Regret is Stockfish win-rate regret in percentage points (lower is better).", "",
             f"## Substituting cheaper models for {reference}", "",
             "Positive difference = worse than the reference model.", "",
             "| role | model | cell | n | regret diff | 95% CI | same move |",
             "|---|---|---|---|---|---|---|"]
    for c in comparisons:
        agree = "" if c["move_agree_pct"] is None else f"{c['move_agree_pct']:.0f}%"
        lines.append(f"| {c['role']} | {c['model']} | {c['cell']} | {c['n']} | "
                     f"{c['regret_diff']:+.2f} | {fmt_ci(c['ci'])} | {agree} |")
    lines += ["", "## Failure, child-failure and truncation rates", "",
              "| agent | failed decisions (scored as random) | one-ply children failed | Queen reads truncated |",
              "|---|---|---|---|"]
    for agent, e in sorted(report["rates"].items()):
        lines.append(f"| {agent} | {pct(e['failed'], e['decisions'])} | "
                     f"{pct(e['failed_children'], e['children'])} | {pct(e['truncated'], e['reads'])} |")
    ts = report["tree_sources"]
    if ts:
        dist = ", ".join(f"{k}: {v}" for k, v in ts["queen_children_dist"].items())
        lines += ["", "## Where the shared tree's children come from", "",
                  f"Positions: {ts['positions']}. Children supplied by Queen (rest topped up by "
                  f"move_priority), count of positions by number: {dist}.",
                  f"BEST_MOVE legal: {ts['best_move_legal_pct']:.0f}%. PROMISING_MOVES written per "
                  f"position: {ts['mean_promising_written']:.2f}, legal: {ts['mean_promising_legal']:.2f} "
                  f"({ts['promising_illegal_pct']:.0f}% illegal). Distinct legal root moves in "
                  f"ANALYSIS: {ts['mean_analysis_moves']:.2f}."]
    lines += ["", "## Writer output Queen can read", "", "| writer | readable |", "|---|---|"]
    for model, c in sorted(report["compliance"].items()):
        lines.append(f"| {model} | {c['ok']}/{c['total']} ({c['pct']:.0f}%) |")
    lines += ["", "## API cost by model and role", "",
              "| model/role | calls | errors | refusals | $ | $/call | mean in | mean out |",
              "|---|---|---|---|---|---|---|---|"]
    for name, c in report["costs"].items():
        lines.append(f"| {name} | {c['calls']} | {c['errors']} | {c['refusals']} | {c['usd']:.2f} | "
                     f"{c['usd_per_call']:.4f} | {c['mean_in']:.0f} | {c['mean_out']:.0f} |")
    lines += ["", "## GPU", "", f"Queen: {report['queen_gpu']}", "", f"Qwen: {report['qwen_gpu']}",
              "", "## All cells", "",
              "| cell | n | regret | 95% CI | regret (successes) | fail% | child fail% | trunc% | top-1% |",
              "|---|---|---|---|---|---|---|---|---|"]
    def opt(value, fmt):
        return "–" if value is None else format(value, fmt)
    for c in table:
        lines.append(f"| {c['cell']} | {c['n']} | {c['regret']:.2f} | {fmt_ci(c['ci'])} | "
                     f"{opt(c['regret_ok'], '.2f')} | {c['fail_pct']:.0f} | "
                     f"{opt(c['child_fail_pct'], '.0f')} | {opt(c['trunc_pct'], '.0f')} | "
                     f"{c['top1_pct']:.0f} |")
    (pilot.dir / "report.md").write_text("\n".join(lines) + "\n")
    write_samples(pilot, pilot.dir / "samples.md")
    print(f"[report] wrote {pilot.dir / 'report.md'} and samples.md")
