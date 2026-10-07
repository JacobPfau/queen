"""Contamination-free positions and Stockfish regret scoring.

Positions come from fresh Stockfish games with randomized move choice, so no
external LLM can have memorised them and none is in Queen's training data.
Scoring evaluates every legal move once with Stockfish; any chosen move's
regret is then a lookup.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

import chess
import chess.engine

from datagen.self_distill.analysis import expected_winrate
from explain.common import Store, stable_hash

MATE_CP = 100_000


def _cp(score: chess.engine.PovScore, turn: chess.Color) -> int:
    return score.pov(turn).score(mate_score=MATE_CP)


def sample_positions(stockfish: Path, count: int, seed: int, nodes: int = 20_000,
                     min_ply: int = 16, max_ply: int = 70, max_abs_cp: int = 350,
                     min_legal: int = 4) -> list[dict]:
    """One position per randomized game, kept when the game is undecided.

    Moves are drawn from Stockfish's top four with a softmax over win rate
    (temperature 0.08), plus four uniformly random opening plies, so games
    diverge quickly while staying plausible.
    """
    rng = random.Random(seed)
    engine = chess.engine.SimpleEngine.popen_uci(str(stockfish))
    rows, seen = [], set()
    try:
        while len(rows) < count:
            board = chess.Board()
            history: list[str] = []
            target = rng.randint(min_ply, max_ply)
            for ply in range(target):
                if board.is_game_over():
                    break
                if ply < 4:
                    move = rng.choice(list(board.legal_moves))
                else:
                    infos = engine.analyse(board, chess.engine.Limit(nodes=nodes), multipv=4)
                    options = [(info["pv"][0], expected_winrate(_cp(info["score"], board.turn)))
                               for info in infos if info.get("pv")]
                    weights = [math.exp(w / 0.08) for _, w in options]
                    move = rng.choices([m for m, _ in options], weights=weights)[0]
                history.append(board.fen())
                board.push(move)
            if board.is_game_over() or board.legal_moves.count() < min_legal:
                continue
            key = " ".join(board.fen().split()[:4])
            if key in seen:
                continue
            info = engine.analyse(board, chess.engine.Limit(nodes=nodes * 5))
            cp = _cp(info["score"], board.turn)
            if abs(cp) > max_abs_cp:
                continue
            seen.add(key)
            rows.append({
                "position_id": f"p{len(rows):04d}",
                "fen": board.fen(),
                "history": history[-7:],
                "ply": len(history),
                "sf_cp_sampling": cp,
            })
    finally:
        engine.quit()
    return rows


class Scorer:
    """Stockfish win rate of every legal move, cached per position."""

    def __init__(self, stockfish: Path, store_path: Path, nodes_per_move: int = 200_000):
        self.stockfish = stockfish
        self.store = Store(store_path)
        self.nodes = nodes_per_move

    def table(self, fen: str) -> dict[str, float]:
        key = stable_hash([fen, self.nodes])
        row = self.store.get(key)
        if row is not None:
            return row["winrates"]
        board = chess.Board(fen)
        engine = chess.engine.SimpleEngine.popen_uci(str(self.stockfish))
        try:
            winrates = {}
            for move in board.legal_moves:
                engine.configure({"Clear Hash": None})
                info = engine.analyse(board, chess.engine.Limit(nodes=self.nodes),
                                      root_moves=[move])
                winrates[move.uci()] = expected_winrate(_cp(info["score"], board.turn))
        finally:
            engine.quit()
        self.store.put(key, {"fen": fen, "nodes": self.nodes, "winrates": winrates})
        return winrates

    def regret(self, fen: str, uci: str | None) -> float | None:
        if uci is None:
            return None
        table = self.table(fen)
        return max(table.values()) - table[uci]

    def uniform_regret(self, fen: str) -> float:
        """Expected regret of a uniformly random legal move: the score of a
        failed decision (its exact expectation, so it adds no sampling noise)."""
        table = self.table(fen)
        return max(table.values()) - sum(table.values()) / len(table)

    def best(self, fen: str) -> str:
        table = self.table(fen)
        return max(table, key=table.get)
