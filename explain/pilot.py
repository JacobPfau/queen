"""Pilot of the explanation-utility experiment (see claude/experiment_choices.md).

Run ``python -m explain.pilot --config configs/explain/pilot.yaml advance``
repeatedly. Each call does every step whose inputs exist, and when Queen or
Qwen output is missing it writes request files and prints the GPU-worker
command to run (explain/gpu.py). API steps first print a spend projection and
stop unless ``--yes`` is given; the hard cap in the config is enforced on
every call.

Pilot scope: depth 0 and 1, one shared depth-1 tree per position (children are
Queen's top three by its numeric prior: the shared-tree control), one-ply
search over those children, and every external-LLM role run with each
configured model so cheaper models can be compared with Opus.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import chess
import yaml

from datagen.self_distill.analysis import field_map, legal_root_candidates
from datagen.tree.moves import move_priority
from explain import hce, prompts
from explain.common import (
    Store, absolute_to_queen, child_fen, child_history, heads_pov, human,
    minimax_heads, parse_heads, parse_san_or_uci, pov_to_absolute, prose_pov,
    prose_ranking, read_jsonl, render_heads, render_ranking, stable_hash,
    stable_seed, write_jsonl,
)
from explain.llm import Caller, ModelSpec
from explain.positions import Scorer, sample_positions

QUEEN_READ_TOKENS = 512
QUEEN_PREFIX_CHAR_LIMIT = 9_000   # keeps prompt + prefix + heads under 4096 tokens
JSON_OBJECT = re.compile(r"\{.*\}", re.S)


def words(text: str) -> int:
    return len(text.split())


class Pilot:
    def __init__(self, config_path: Path):
        self.cfg = yaml.safe_load(Path(config_path).read_text())
        self.dir = Path(self.cfg["workdir"])
        self.dir.mkdir(parents=True, exist_ok=True)
        self.queen = Store(self.dir / "queen_store.jsonl")
        self.qwen = Store(self.dir / "qwen_store.jsonl")
        specs = {name: ModelSpec(name=name, **spec) for name, spec in self.cfg["models"].items()}
        self.models = list(specs)
        self.llm = Caller(specs, self.dir / "llm_cache.jsonl",
                          self.cfg["max_api_spend_usd"], self.cfg.get("api_workers", 16))
        self.writers = self.cfg["roles"]["hybrid_writers"]
        self.consolidators = ["qwen"] + self.cfg["roles"]["external_consolidators"]
        self.judge = self.cfg["roles"]["reference_reader"]   # reads every text
        self.readers = self.cfg["roles"]["readers"]           # read the core texts
        self.choosers = self.cfg["roles"]["choosers"]
        self._memo: dict = {}

    def reset(self) -> None:
        """Drop memoized views; call after any store gains new results."""
        self._memo.clear()

    def _memoized(self, name: str, position: dict, build):
        key = (name, position["position_id"])
        if key not in self._memo:
            self._memo[key] = build()
        return self._memo[key]

    # ------------------------------------------------------------ positions

    @property
    def positions(self) -> list[dict]:
        if "positions" not in self._memo:
            path = self.dir / "positions.jsonl"
            if not path.exists():
                rows = sample_positions(Path(self.cfg["stockfish"]), self.cfg["positions"],
                                        self.cfg["seed"])
                write_jsonl(path, rows)
            self._memo["positions"] = read_jsonl(path)
        return self._memo["positions"]

    def r0_move(self, position: dict) -> str:
        return self._memoized("r0", position, lambda: hce.choose(position["fen"])[0])

    # ---------------------------------------------------------------- Queen

    def gen_key(self, fen: str) -> str:
        return stable_hash(["gen", fen, self.cfg["seed"]])

    def gen_request(self, fen: str, history: list[str]) -> dict:
        return {"key": self.gen_key(fen), "fen": fen, "history": history,
                "seed": stable_seed("gen", fen, self.cfg["seed"]), "max_tokens": 2048}

    def generation(self, fen: str) -> str | None:
        row = self.queen.get(self.gen_key(fen))
        return row["text"] if row else None

    def read_request(self, fen: str, history: list[str], prose: str) -> dict:
        # Ending the pre-fill at BEST_MOVE makes Queen commit to a reading of the
        # given prose; pre-filling only ANALYSIS lets it write its own analysis.
        prefix = f"ANALYSIS:\n{prose[:QUEEN_PREFIX_CHAR_LIMIT]}\nBEST_MOVE:"
        return {"key": stable_hash(["read", fen, prefix]), "fen": fen, "history": history,
                "prefix": prefix, "seed": stable_seed("read", fen, prefix),
                "max_tokens": QUEEN_READ_TOKENS, "truncated": len(prose) > QUEEN_PREFIX_CHAR_LIMIT}

    def queen_read(self, request: dict) -> dict | None:
        row = self.queen.get(request["key"])
        if row is None:
            return None
        heads = parse_heads(request["fen"], request["prefix"] + row["text"])
        heads["truncated"] = request["truncated"]
        return heads

    # ------------------------------------------------------------- the tree

    def children(self, position: dict) -> list[str] | None:
        """Shared tree: Queen's top three root candidates, topped up by move order."""
        return self._memoized("children", position, lambda: self._children(position))

    def _children(self, position: dict) -> list[str] | None:
        fen = position["fen"]
        generation = self.generation(fen)
        if generation is None:
            return None
        moves = [move.uci() for move in legal_root_candidates(fen, generation)]
        board = chess.Board(fen)
        for move in sorted(board.legal_moves, key=lambda m: move_priority(board, m)):
            if len(moves) >= 3:
                break
            if move.uci() not in moves:
                moves.append(move.uci())
        return moves[:3]

    # --------------------------------------------------------------- texts

    def writer_text(self, raw: str, fen: str) -> dict:
        """A writer's absolute-token output -> Queen-vocabulary views."""
        try:
            pov = absolute_to_queen(raw, fen)
        except ValueError as error:
            return {"ok": False, "error": f"vocabulary: {error}"[:300], "raw": raw}
        prose = prose_pov(pov)
        if not prose:
            return {"ok": False, "error": "no ANALYSIS field", "raw": raw}
        has_heads = "BEST_MOVE" in field_map(pov)
        return {"ok": True, "prose": prose, "heads": parse_heads(fen, pov) if has_heads else None,
                "raw": raw}

    def hybrid_request(self, writer: str, fen: str) -> dict | None:
        generation = self.generation(fen)
        if generation is None:
            return None
        heads = parse_heads(fen, generation)
        system, user = prompts.hybrid_writer(
            fen, render_heads(fen, heads), pov_to_absolute(heads_pov(generation), fen),
            max(80, words(human(prose_pov(generation), fen))),
        )
        return {"model": writer, "system": system, "user": user, "tag": "writer"}

    def hybrid_text(self, writer: str, fen: str) -> dict | None:
        request = self.hybrid_request(writer, fen)
        if request is None:
            return None
        row = self.llm.store.get(self.llm.key(**{k: request[k] for k in ("model", "system", "user", "tag")}))
        if row is None or row.get("error"):
            return None
        text = self.writer_text(row["text"], fen)
        if text["ok"]:
            text["heads"] = parse_heads(fen, self.generation(fen))  # hybrid R4 = hybrid prose + Queen heads
        return text

    def consolidation_request(self, position: dict, source: str, variant: str,
                              consolidator: str) -> dict | None:
        fen = position["fen"]
        kids = self.children(position)
        if kids is None:
            return None
        blocks, prose_words = [], []
        for uci in kids:
            cfen = child_fen(fen, uci)
            generation = self.generation(cfen)
            if generation is None:
                return None
            heads = parse_heads(cfen, generation)
            if source == "q":
                body = generation if variant == "full" else prose_pov(generation)
                text_abs = pov_to_absolute(body, cfen)
                prose_words.append(words(human(prose_pov(generation), cfen)))
            else:
                hybrid = self.hybrid_text(source[2:], cfen)
                if hybrid is None or not hybrid["ok"]:
                    return None
                text_abs = pov_to_absolute(hybrid["prose"], cfen)
                if variant == "full":
                    text_abs += "\n" + pov_to_absolute(heads_pov(generation), cfen)
                prose_words.append(words(human(hybrid["prose"], cfen)))
            blocks.append({"uci": uci, "fen": cfen, "text_abs": text_abs,
                           "root_winrate": None if heads["winrate"] is None else 1 - heads["winrate"]})
        system, user = prompts.consolidator(fen, variant, blocks,
                                            max(80, sum(prose_words) // len(prose_words)))
        return self._writer_request(consolidator, system, user, "consolidator")

    def rewrite_request(self, position: dict, variant: str, consolidator: str) -> dict | None:
        fen = position["fen"]
        generation = self.generation(fen)
        if generation is None:
            return None
        body = generation if variant == "full" else prose_pov(generation)
        system, user = prompts.rewrite(fen, variant, pov_to_absolute(body, fen),
                                       max(80, words(human(prose_pov(generation), fen))))
        return self._writer_request(consolidator, system, user, "rewrite")

    def _writer_request(self, model: str, system: str, user: str, tag: str) -> dict:
        if model == "qwen":
            return {"qwen": True, "key": stable_hash(["qwen", system, user]),
                    "system": system, "user": user}
        return {"model": model, "system": system, "user": user, "tag": tag}

    def writer_output(self, request: dict | None, fen: str) -> dict | None:
        if request is None:
            return None
        if request.get("qwen"):
            row = self.qwen.get(request["key"])
        else:
            row = self.llm.store.get(self.llm.key(request["model"], request["system"],
                                                  request["user"], None, request["tag"]))
        if row is None or row.get("error"):
            return None
        return self.writer_text(row["text"], fen)

    def root_texts(self, position: dict) -> dict[str, dict]:
        """Every root-level text for the depth axis, keyed by text id."""
        return self._memoized("roots", position, lambda: self._root_texts(position))

    def _root_texts(self, position: dict) -> dict[str, dict]:
        fen = position["fen"]
        texts = {}
        generation = self.generation(fen)
        if generation is None:
            return texts
        texts["q/d0"] = {"ok": True, "prose": prose_pov(generation),
                         "heads": parse_heads(fen, generation)}
        kids = self.children(position)
        child_heads = {}
        for uci in kids:
            child_generation = self.generation(child_fen(fen, uci))
            if child_generation is not None:
                child_heads[uci] = parse_heads(child_fen(fen, uci), child_generation)
        if len(child_heads) == len(kids):
            texts["q/d1/minimax"] = {"ok": True, "prose": None, "heads": minimax_heads(fen, child_heads)}
        for variant in ("prose", "full"):
            for cons in self.consolidators:
                out = self.writer_output(self.consolidation_request(position, "q", variant, cons), fen)
                if out is not None:
                    texts[f"q/d1/{cons}/{variant}"] = out
                out = self.writer_output(self.rewrite_request(position, variant, cons), fen)
                if out is not None:
                    texts[f"q/rw/{cons}/{variant}"] = out
            for writer in self.writers:
                out = self.writer_output(
                    self.consolidation_request(position, f"h-{writer}", variant, "qwen"), fen)
                if out is not None:
                    texts[f"h-{writer}/d1/qwen/{variant}"] = out
        for writer in self.writers:
            out = self.hybrid_text(writer, fen)
            if out is not None:
                texts[f"h-{writer}/d0"] = out
        return texts

    def child_texts(self, position: dict) -> dict[str, dict[str, dict]]:
        """Per child: {'q': Queen's analysis, 'h-<writer>': hybrid prose}."""
        return self._memoized("kids", position, lambda: self._child_texts(position))

    def _child_texts(self, position: dict) -> dict[str, dict[str, dict]]:
        out = {}
        for uci in self.children(position) or []:
            cfen = child_fen(position["fen"], uci)
            generation = self.generation(cfen)
            if generation is None:
                continue
            entry = {"q": {"ok": True, "prose": prose_pov(generation),
                           "heads": parse_heads(cfen, generation)}}
            for writer in self.writers:
                hybrid = self.hybrid_text(writer, cfen)
                if hybrid is not None:
                    entry[f"h-{writer}"] = hybrid
            out[uci] = entry
        return out

    # ---------------------------------------------------------------- cells

    def reader_plan(self, text_id: str) -> list[str]:
        """Which external readers read a root text (the judge reads all)."""
        core = text_id in ("q/d0", "q/d1/qwen/prose", "q/d1/qwen/full")
        return [r for r in self.readers if r == self.judge or core]

    def cells(self, position: dict) -> list[dict]:
        """Every decision cell for one position whose inputs are available.

        A cell is {kind, rung, text, agent, fen_shown, effort}; ``agent`` is
        hce | mech | queen | <external model>. kind: depth (decide from one
        root text), oneply (score the shared tree's children), chooser (R′).
        """
        cells = [{"kind": "depth", "rung": "R0", "text": None, "agent": "hce"},
                 {"kind": "oneply", "rung": "R0", "text": None, "agent": "hce"}]
        roots = self.root_texts(position)
        for text_id, text in roots.items():
            if not text["ok"]:
                continue
            if text.get("prose"):
                cells.append({"kind": "depth", "rung": "R1", "text": text_id, "agent": "mech"})
                cells.append({"kind": "depth", "rung": "R2", "text": text_id, "agent": "queen"})
                for reader in self.reader_plan(text_id):
                    cells.append({"kind": "depth", "rung": "R2", "text": text_id, "agent": reader})
            if text.get("heads"):
                cells.append({"kind": "depth", "rung": "R3", "text": text_id, "agent": "mech"})
                if text.get("prose"):
                    for reader in self.reader_plan(text_id):
                        cells.append({"kind": "depth", "rung": "R4", "text": text_id, "agent": reader})
        if "q/d0" in roots:
            for reader in self.readers:
                cells.append({"kind": "depth", "rung": "ctrl", "text": None, "agent": reader})
                for rung in ("R2", "R4"):
                    cells.append({"kind": "depth", "rung": rung, "text": "q/d0", "agent": reader,
                                  "fen_shown": False})
        kids = self.child_texts(position)
        if kids and len(kids) == len(self.children(position) or []):
            cells.append({"kind": "oneply", "rung": "R3", "text": "q", "agent": "mech"})
            sources = ["q"] + [f"h-{w}" for w in self.writers]
            for source in sources:
                if not all(kids[u].get(source, {}).get("ok") for u in kids):
                    continue
                cells.append({"kind": "oneply", "rung": "R2", "text": source, "agent": "queen"})
                for reader in self.readers:
                    if source != "q" and reader != self.judge:
                        continue
                    for rung in ("R2", "R4"):
                        cells.append({"kind": "oneply", "rung": rung, "text": source, "agent": reader})
            for reader in self.readers:
                cells.append({"kind": "oneply", "rung": "ctrl", "text": None, "agent": reader})
                for rung in ("R2", "R4"):
                    cells.append({"kind": "oneply", "rung": rung, "text": "q", "agent": reader,
                                  "fen_shown": False})
        for model in self.choosers:
            cells.append({"kind": "chooser", "rung": "R0", "text": None, "agent": model})
            if "q/d0" in roots:
                for rung in ("R1", "R2", "R3", "R4"):
                    cells.append({"kind": "chooser", "rung": rung, "text": "q/d0", "agent": model})
                    cells.append({"kind": "chooser", "rung": rung, "text": "q/d0", "agent": model,
                                  "fen_shown": False})
                for effort in self.cfg["effort_sweep"].get(model, []):
                    cells.append({"kind": "chooser", "rung": "R0", "text": None, "agent": model,
                                  "effort": effort})
                    cells.append({"kind": "chooser", "rung": "R4", "text": "q/d0", "agent": model,
                                  "effort": effort})
            for rung, text_id in (("R1", "q/d1/qwen/prose"), ("R2", "q/d1/qwen/prose"),
                                  ("R3", "q/d1/minimax"), ("R4", "q/d1/qwen/full")):
                if roots.get(text_id, {}).get("ok"):
                    cells.append({"kind": "chooser", "rung": rung, "text": text_id, "agent": model})
            if model == self.judge:
                for text_id, text in roots.items():
                    if text_id in ("q/d0", "q/d1/qwen/prose", "q/d1/qwen/full", "q/d1/minimax"):
                        continue
                    if text["ok"] and text.get("prose"):
                        cells.append({"kind": "chooser", "rung": "R2", "text": text_id, "agent": model})
                        if text.get("heads"):
                            cells.append({"kind": "chooser", "rung": "R4", "text": text_id,
                                          "agent": model})
        for cell in cells:
            cell.setdefault("fen_shown", True)
            cell.setdefault("effort", None)
        return cells

    # ------------------------------------------------- evidence and requests

    def evidence(self, fen: str, rung: str, text: dict | None) -> str | None:
        if rung in ("R0", "ctrl") or text is None:
            return None
        if rung == "R1":
            return prompts.evidence_block(ranking=render_ranking(fen, prose_ranking(fen, text["prose"])))
        prose = human(text["prose"], fen) if rung in ("R2", "R4") else None
        heads = render_heads(fen, text["heads"]) if rung in ("R3", "R4") else None
        return prompts.evidence_block(prose=prose, heads=heads)

    def external_request(self, fen: str, cell: dict, text: dict | None) -> dict:
        build = prompts.chooser if cell["kind"] == "chooser" else prompts.reader
        system, user = build(fen, self.evidence(fen, cell["rung"], text), cell["fen_shown"])
        return {"model": cell["agent"], "system": system, "user": user,
                "effort": cell["effort"], "tag": "chooser" if cell["kind"] == "chooser" else "reader"}

    def cell_requests(self, position: dict, cell: dict) -> list[tuple[str, dict, str]]:
        """(fen, request, kind) for every model call a cell needs.

        kind is 'api' or 'queen'. oneply cells need one call per child.
        """
        fen, history = position["fen"], position["history"]
        agent = cell["agent"]
        if agent in ("hce", "mech"):
            return []
        if cell["kind"] == "oneply":
            out = []
            for uci, texts in self.child_texts(position).items():
                cfen = child_fen(fen, uci)
                text = texts.get(cell["text"]) if cell["text"] else None
                if agent == "queen":
                    out.append((cfen, self.read_request(cfen, child_history(history, fen),
                                                        text["prose"]), "queen"))
                else:
                    out.append((cfen, self.external_request(cfen, cell, text), "api"))
            return out
        text = self.root_texts(position).get(cell["text"]) if cell["text"] else None
        if agent == "queen":
            return [(fen, self.read_request(fen, history, text["prose"]), "queen")]
        return [(fen, self.external_request(fen, cell, text), "api")]

    # --------------------------------------------------------------- parsing

    def parse_external(self, fen: str, row: dict | None, kind: str) -> dict:
        if row is None:
            return {"status": "missing"}
        if row.get("error"):
            return {"status": "error", "error": row["error"]}
        if row.get("stop_reason") == "refusal":
            return {"status": "refusal"}
        match = JSON_OBJECT.search(row["text"])
        try:
            data = json.loads(match.group(0)) if match else None
        except json.JSONDecodeError:
            data = None
        if not isinstance(data, dict):
            return {"status": "unparseable", "raw": row["text"][:300]}
        if kind == "chooser":
            move = parse_san_or_uci(fen, str(data.get("move", "")))
            return {"status": "ok" if move else "illegal", "move": move,
                    "reason": data.get("reason")}
        probs = {}
        for name, value in (data.get("move_probs") or {}).items():
            move = parse_san_or_uci(fen, str(name))
            if move is not None and isinstance(value, (int, float)):
                probs[move] = float(value)
        win = data.get("win_prob")
        win = float(win) if isinstance(win, (int, float)) and 0 <= win <= 1 else None
        best = max(probs, key=probs.get) if probs else None
        return {"status": "ok" if best or win is not None else "empty", "move": best,
                "probs": probs, "winrate": win, "reason": data.get("reason")}

    def answer(self, fen: str, request: dict, kind: str, cell_kind: str) -> dict:
        if kind == "queen":
            heads = self.queen_read(request)
            if heads is None:
                return {"status": "missing"}
            return {"status": "ok" if heads["best"] or heads["winrate"] is not None else "empty",
                    "move": heads["best"], "winrate": heads["winrate"],
                    "truncated": heads.get("truncated")}
        row = self.llm.store.get(self.llm.key(request["model"], request["system"],
                                              request["user"], request["effort"], request["tag"]))
        return self.parse_external(fen, row, "chooser" if cell_kind == "chooser" else "reader")

    def decide(self, position: dict, cell: dict) -> dict:
        """The move a cell plays, or a failure status (scored with the R0 fallback)."""
        fen = position["fen"]
        rung, agent = cell["rung"], cell["agent"]
        if agent == "hce":
            if cell["kind"] == "depth":
                return {"status": "ok", "move": self.r0_move(position)}
            values = {uci: hce.child_cp(fen, uci) for uci in self.children(position)}
            return {"status": "ok", "move": max(values, key=values.get)}
        if agent == "mech":
            if cell["kind"] == "oneply":
                text = self.root_texts(position)["q/d1/minimax"]
                return {"status": "ok" if text["heads"]["best"] else "empty",
                        "move": text["heads"]["best"]}
            text = self.root_texts(position)[cell["text"]]
            if rung == "R1":
                ranking = prose_ranking(fen, text["prose"])
                return {"status": "ok" if ranking else "empty", "move": ranking[0] if ranking else None}
            return {"status": "ok" if text["heads"]["best"] else "empty", "move": text["heads"]["best"]}
        requests = self.cell_requests(position, cell)
        answers = [self.answer(cfen, request, kind, cell["kind"]) for cfen, request, kind in requests]
        if cell["kind"] != "oneply":
            return answers[0]
        # one-ply search: the child whose value (from the side to move) is highest.
        values = {}
        for uci, answer in zip(self.children(position), answers):
            if answer.get("winrate") is not None:
                values[uci] = 1.0 - answer["winrate"]
        if not values:
            statuses = sorted({a["status"] for a in answers})
            return {"status": "empty" if statuses == ["ok"] else "/".join(statuses)}
        return {"status": "ok", "move": max(values, key=values.get), "child_values": values,
                "missing_children": len(answers) - len(values)}

    # ---------------------------------------------------------------- stages

    def queen_requests(self) -> list[dict]:
        requests = []
        for position in self.positions:
            fen, history = position["fen"], position["history"]
            if self.generation(fen) is None:
                requests.append(self.gen_request(fen, history))
                continue
            for uci in self.children(position):
                cfen = child_fen(fen, uci)
                if self.generation(cfen) is None:
                    requests.append(self.gen_request(cfen, child_history(history, fen)))
            for cell in self.cells(position):
                for _, request, kind in self.cell_requests(position, cell):
                    if kind == "queen" and request["key"] not in self.queen:
                        requests.append(request)
        return requests

    def writer_requests(self) -> tuple[list[dict], list[dict]]:
        """(qwen requests, external writer requests) whose inputs are ready."""
        qwen, api = [], []
        for position in self.positions:
            fen = position["fen"]
            if self.generation(fen) is None:
                continue
            kids = self.children(position)
            for writer in self.writers:
                for node in [fen] + [child_fen(fen, uci) for uci in kids]:
                    request = self.hybrid_request(writer, node)
                    if request is not None:
                        api.append(request)
            for variant in ("prose", "full"):
                candidates = [self.consolidation_request(position, "q", variant, c)
                              for c in self.consolidators]
                candidates += [self.rewrite_request(position, variant, c) for c in self.consolidators]
                candidates += [self.consolidation_request(position, f"h-{w}", variant, "qwen")
                               for w in self.writers]
                for request in candidates:
                    if request is None:
                        continue
                    (qwen if request.get("qwen") else api).append(request)
        return qwen, api

    def api_cell_requests(self) -> list[dict]:
        requests = []
        for position in self.positions:
            for cell in self.cells(position):
                if cell["agent"] in ("hce", "mech", "queen"):
                    continue
                for _, request, _ in self.cell_requests(position, cell):
                    requests.append(request)
        return requests

    def projection(self, requests: list[dict]) -> dict:
        """Projected cost of the uncached requests, per model."""
        out_tokens = self.cfg["projected_output_tokens"]
        by_model = defaultdict(lambda: {"calls": 0, "usd": 0.0})
        for request in requests:
            key = self.llm.key(request["model"], request["system"], request["user"],
                               request.get("effort"), request.get("tag", ""))
            row = self.llm.store.get(key)
            if row is not None and not row.get("error"):
                continue
            spec = self.llm.specs[request["model"]]
            tokens_in = (len(request["system"]) + len(request["user"])) / 3.2
            tokens_out = out_tokens[request.get("tag", "reader")]
            if request.get("effort") == "high":
                tokens_out *= 2.5
            entry = by_model[request["model"]]
            entry["calls"] += 1
            entry["usd"] += spec.cost(tokens_in, tokens_out)
        return dict(by_model)

    def run_api(self, requests: list[dict], label: str, yes: bool) -> bool:
        unique = list({stable_hash(r): r for r in requests}.values())
        projection = self.projection(unique)
        total = sum(entry["usd"] for entry in projection.values())
        print(f"[{label}] {len(unique)} requests; uncached projection: "
              + ", ".join(f"{m}: {e['calls']} calls ${e['usd']:.2f}" for m, e in projection.items())
              + f" (total ${total:.2f}; spent so far ${self.llm.ledger.spent:.2f}"
              f" of cap ${self.llm.ledger.max_spend:.0f})")
        if not projection:
            return True
        if self.llm.ledger.spent + total > self.llm.ledger.max_spend:
            print(f"[{label}] projection exceeds the cap; not running")
            return False
        if not yes:
            print(f"[{label}] rerun with --yes to spend")
            return False
        results = self.llm.map(unique)
        failures = sum(bool(r.get("error")) for r in results)
        print(f"[{label}] done; {failures} failures; spent ${self.llm.ledger.spent:.2f}")
        return True

    def gpu_hint(self, worker: str, requests: list[dict]) -> None:
        path = self.dir / f"{worker}_requests.jsonl"
        write_jsonl(path, requests)
        print(f"[{worker}] {len(requests)} requests pending in {path}")

    def advance(self, yes: bool) -> None:
        print(f"[positions] {len(self.positions)}")
        qwen, writers = self.writer_requests()
        if writers:
            self.run_api(writers, "writers", yes)
            self.reset()
            qwen, _ = self.writer_requests()
        qwen = [r for r in qwen if r["key"] not in self.qwen]
        queen = self.queen_requests()  # after writers: Queen also reads their texts
        if queen:
            self.gpu_hint("queen", queen)
        if qwen:
            self.gpu_hint("qwen", list({r["key"]: r for r in qwen}.values()))
        self.run_api(self.api_cell_requests(), "readers+choosers", yes)
        self.reset()
        api = list({stable_hash(r): r for r in self.api_cell_requests()}.values())
        api_left = len(api) - self.llm.cached(api)
        status = {"queen_pending": len(queen), "qwen_pending": len(qwen),
                  "api_pending": api_left, "api_spent_usd": self.llm.ledger.spent}
        (self.dir / "status.json").write_text(json.dumps(status))
        print(f"[advance] {status}")

    # ---------------------------------------------------------------- report

    def decisions(self) -> list[dict]:
        scorer = Scorer(Path(self.cfg["stockfish"]), self.dir / "sf_store.jsonl",
                        self.cfg["oracle_nodes"])
        positions = self.positions
        with ThreadPoolExecutor(max_workers=self.cfg.get("oracle_workers", 8)) as pool:
            list(pool.map(lambda p: scorer.table(p["fen"]), positions))
        rows = []
        for position in positions:
            fen = position["fen"]
            fallback = self.r0_move(position)
            for cell in self.cells(position):
                decision = self.decide(position, cell)
                move = decision.get("move") if decision["status"] == "ok" else None
                rows.append({
                    "position_id": position["position_id"], **cell, **decision,
                    "regret": scorer.regret(fen, move or fallback),
                    "fallback_used": move is None,
                    "sf_best": scorer.best(fen),
                })
        write_jsonl(self.dir / "decisions.jsonl", rows)
        return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("command", choices=["advance", "decide", "report", "status"])
    parser.add_argument("--yes", action="store_true", help="allow API spend")
    args = parser.parse_args()
    pilot = Pilot(args.config)
    if args.command == "advance":
        pilot.advance(args.yes)
    elif args.command == "decide":
        rows = pilot.decisions()
        print(f"[decide] {len(rows)} decisions")
    elif args.command == "report":
        from explain.report import write_report
        write_report(pilot)
    else:
        print(f"positions={len(pilot.positions)} queen={len(pilot.queen.data)} "
              f"qwen={len(pilot.qwen.data)} api_calls={len(pilot.llm.store.data)} "
              f"spent=${pilot.llm.ledger.spent:.2f}")


if __name__ == "__main__":
    sys.exit(main())
