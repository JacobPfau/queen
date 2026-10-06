"""Base evaluator: the repo's hand-crafted evaluation with a capture-only search.

Used for R0 (no Queen input) and wherever a rung has no value signal. It is
deliberately weak relative to Stockfish so it cannot hide Queen's contribution.
"""

from __future__ import annotations

import chess

from datagen.tree.primitives.core.score import to_cp
from datagen.tree.primitives.toplevel import value

MATE_CP = 10_000
PIECE_CP = {chess.PAWN: 100, chess.KNIGHT: 300, chess.BISHOP: 300,
            chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0}


def static_cp(board: chess.Board) -> float:
    """Side-to-move centipawns from the hand-crafted evaluation."""
    if board.is_checkmate():
        return -MATE_CP
    if board.is_stalemate() or board.is_insufficient_material():
        return 0.0
    return 100.0 * to_cp(value(board))


def _captures(board: chess.Board) -> list[chess.Move]:
    def gain(move):
        victim = board.piece_at(move.to_square)
        attacker = board.piece_at(move.from_square)
        return (PIECE_CP[victim.piece_type] if victim else 100) * 10 - PIECE_CP[attacker.piece_type]
    return sorted((m for m in board.legal_moves if board.is_capture(m)), key=gain, reverse=True)


def qsearch(board: chess.Board, alpha: float, beta: float, depth: int = 4) -> float:
    """Fail-hard quiescence over captures; full-width when in check."""
    if board.is_checkmate():
        return -MATE_CP
    in_check = board.is_check()
    if not in_check:
        stand = static_cp(board)
        if stand >= beta or depth == 0:
            return stand
        alpha = max(alpha, stand)
    moves = list(board.legal_moves) if in_check else _captures(board)
    if not moves:
        return static_cp(board)
    for move in moves:
        board.push(move)
        score = -qsearch(board, -beta, -alpha, depth - 1)
        board.pop()
        if score >= beta:
            return beta
        alpha = max(alpha, score)
    return alpha


def child_cp(fen: str, uci: str) -> float:
    """Value of playing ``uci`` for the side to move at ``fen``."""
    board = chess.Board(fen)
    board.push_uci(uci)
    return -qsearch(board, -MATE_CP, MATE_CP)


def choose(fen: str) -> tuple[str, dict[str, float]]:
    """R0: one ply over every legal move, each scored by quiescence search."""
    board = chess.Board(fen)
    scores = {move.uci(): child_cp(fen, move.uci()) for move in board.legal_moves}
    return max(scores, key=scores.get), scores
