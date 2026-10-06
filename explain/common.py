"""Shared pieces: JSONL caches, Queen-output views, and text rendering.

Vocabularies:
  * POV tokens (<PIECE_MN><SQUARE_7>...) are what Queen reads and writes.
  * Absolute tokens (<WHITE_KNIGHT><SQUARE_G1>...) are what every *writer*
    (Qwen, external consolidators, hybrid-prose writers) emits, as in the
    self-distill consolidation recipe; ``absolute_to_pov`` turns them into
    Queen's vocabulary.
  * Human text ("white knight g1-f3") is what external *readers* see,
    decoded from POV tokens with ``Translator``.
"""

from __future__ import annotations

import hashlib
import json
import threading
from pathlib import Path
from typing import Any

import chess

from datagen.self_distill.analysis import (
    MOVE,
    expected_winrate,
    field_map,
    parse_critical,
    parse_model_evaluation,
    pov_move,
)
from datagen.self_distill.consolidation import absolute_tokens
from utils.pack_self_distill import absolute_to_pov
from utils.translate_helpers import Translator


def stable_hash(value: Any, size: int = 12) -> str:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"))
    return hashlib.blake2b(text.encode(), digest_size=size).hexdigest()


def stable_seed(*parts: Any) -> int:
    return int(stable_hash(parts, 8), 16) % (2**31 - 1)


class Store:
    """Append-only JSONL map from key to record; safe across threads.

    Every expensive result (a generation, an API call, an engine search) goes
    through a Store, so a rerun never repeats work or spend.
    """

    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.data: dict[str, dict] = {}
        self.lock = threading.Lock()
        if self.path.exists():
            with self.path.open() as handle:
                for line in handle:
                    if line.strip():
                        row = json.loads(line)
                        self.data[row["key"]] = row

    def __contains__(self, key: str) -> bool:
        return key in self.data

    def get(self, key: str) -> dict | None:
        return self.data.get(key)

    def put(self, key: str, record: dict) -> dict:
        row = {"key": key, **record}
        with self.lock:
            self.data[key] = row
            with self.path.open("a") as handle:
                handle.write(json.dumps(row, separators=(",", ":")) + "\n")
                handle.flush()
        return row

    def values(self) -> list[dict]:
        return list(self.data.values())


def read_jsonl(path: Path) -> list[dict]:
    with Path(path).open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, separators=(",", ":")) + "\n")
    temporary.replace(path)


# ------------------------------------------------------------- board helpers

def child_fen(fen: str, uci: str) -> str:
    board = chess.Board(fen)
    board.push_uci(uci)
    return board.fen()


def child_history(history: list[str], fen: str) -> list[str]:
    return (list(history) + [fen])[-7:]


def san(fen: str, uci: str) -> str:
    board = chess.Board(fen)
    return board.san(chess.Move.from_uci(uci))


def legal_san(fen: str) -> list[str]:
    board = chess.Board(fen)
    return sorted(board.san(move) for move in board.legal_moves)


def parse_san_or_uci(fen: str, text: str) -> str | None:
    """Return the UCI of a legal move written as SAN or UCI, else None."""
    board = chess.Board(fen)
    text = text.strip().strip(".").strip()
    for parse in (board.parse_san, board.parse_uci):
        try:
            move = parse(text)
        except ValueError:
            continue
        if move in board.legal_moves:
            return move.uci()
    return None


def side_name(fen: str) -> str:
    return "White" if chess.Board(fen).turn == chess.WHITE else "Black"


# ------------------------------------------------------ views of Queen output

def prose_pov(generation: str) -> str:
    """The ANALYSIS field (or the whole text when the fields are missing)."""
    fields = field_map(generation)
    return fields.get("ANALYSIS", generation if not fields else "").strip()


def heads_pov(generation: str) -> str:
    """The structured head fields R3 sees, in Queen's own vocabulary."""
    fields = field_map(generation)
    return "\n".join(
        f"{name}: {fields[name]}"
        for name in ("BEST_MOVE", "CRITICAL_LINE", "EVALUATION")
        if name in fields
    )


def prose_ranking(fen: str, prose: str) -> list[str]:
    """R1: legal root moves in order of first mention in the prose (no cap)."""
    board = chess.Board(fen)
    ranking = []
    for atom in MOVE.finditer(prose):
        move, _ = pov_move(atom, board.copy(stack=False), board.turn)
        if move is not None and move.uci() not in ranking:
            ranking.append(move.uci())
    return ranking


def parse_heads(fen: str, generation: str) -> dict:
    """R3: best move, legal PV prefix, and side-to-move win rate, or Nones."""
    board = chess.Board(fen)
    best = None
    for atom in MOVE.finditer(field_map(generation).get("BEST_MOVE", "")):
        move, _ = pov_move(atom, board, board.turn)
        best = move.uci() if move else None
        break
    critical = parse_critical(fen, generation)
    pv = [step["uci"] for step in critical["legal_steps"]]
    evaluation, error = parse_model_evaluation(generation, board.turn)
    if best is None and pv:
        best = pv[0]
    return {
        "best": best,
        "pv": pv,
        "winrate": evaluation["winrate"] if evaluation else None,
        "eval_display": evaluation["root_pov"] if evaluation else None,
        "eval_error": error,
    }


def minimax_heads(fen: str, children: dict[str, dict]) -> dict:
    """R3 at depth 1: back up the children's numeric heads by minimax.

    ``children`` maps root move UCI -> parse_heads() of that child, whose win
    rate is from the opponent's point of view.
    """
    scored = {
        move: 1.0 - heads["winrate"]
        for move, heads in children.items()
        if heads["winrate"] is not None
    }
    if not scored:
        return {"best": None, "pv": [], "winrate": None, "eval_display": None,
                "eval_error": "no child evaluation parsed"}
    best = max(scored, key=scored.get)
    return {
        "best": best,
        "pv": [best, *children[best]["pv"]],
        "winrate": scored[best],
        "eval_display": f"win rate {100 * scored[best]:.0f}%",
        "eval_error": None,
        "child_winrates": scored,
    }


# ------------------------------------------------------------- vocabularies

def pov_to_absolute(text: str, fen: str) -> str:
    return absolute_tokens(text, chess.Board(fen).turn)


def absolute_to_queen(text: str, fen: str) -> str:
    """Writer output (absolute tokens) -> Queen's POV vocabulary; raises on junk."""
    return absolute_to_pov(text, fen)


def human(text_pov: str, fen: str) -> str:
    """POV-token text -> readable text for an external model."""
    return Translator(chess.Board(fen).turn).decode_absolute(text_pov)


def render_line(fen: str, ucis: list[str]) -> str:
    """A legal UCI line as numbered SAN, e.g. '12. Nf3 d5 13. c4'."""
    board = chess.Board(fen)
    parts = []
    for uci in ucis:
        move = chess.Move.from_uci(uci)
        if move not in board.legal_moves:
            break
        if board.turn == chess.WHITE:
            parts.append(f"{board.fullmove_number}.")
        elif not parts:
            parts.append(f"{board.fullmove_number}...")
        parts.append(board.san(move))
        board.push(move)
    return " ".join(parts)


def render_heads(fen: str, heads: dict) -> str:
    """Numeric heads as plain text for an external model."""
    lines = []
    if heads.get("best"):
        lines.append(f"Best move: {san(fen, heads['best'])}")
    if heads.get("pv"):
        lines.append(f"Critical line: {render_line(fen, heads['pv'])}")
    if heads.get("winrate") is not None:
        lines.append(
            f"Evaluation: {heads.get('eval_display')} for {side_name(fen)} "
            f"(expected score {100 * heads['winrate']:.0f}% for {side_name(fen)})"
        )
    return "\n".join(lines) if lines else "(no parseable heads)"


def render_ranking(fen: str, ranking: list[str]) -> str:
    if not ranking:
        return "(the analysis mentions no legal move for the side to move)"
    return ", ".join(san(fen, uci) for uci in ranking)


def winrate_from_cp(cp: float) -> float:
    return expected_winrate(round(cp))

