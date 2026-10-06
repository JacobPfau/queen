"""Prompts for every external-LLM and consolidator role in the pilot.

Each builder returns ``(system, user)``. Writers (consolidators and hybrid
writers) emit the absolute token vocabulary so that Queen can read their
output; readers and choosers see human-readable text and answer in SAN.
The consolidator prompts adapt the self-distill "faithful editor" recipe
(datagen/self_distill/consolidation.py) with the Stockfish-boundary
instructions removed: this experiment allows legality truncation only.
"""

from __future__ import annotations

import chess

from datagen.self_distill.consolidation import absolute_move_tokens
from explain.common import legal_san, side_name

VOCABULARY = """Use only this absolute machine vocabulary:
- squares: <SQUARE_E4>;
- pieces: <WHITE_PAWN>, <BLACK_BISHOP>, and analogous colored piece tokens;
- players: <WHITE> and <BLACK>;
- files, ranks, and diagonals: <FILE_E>, <RANK_4>, <DIAGONAL_A1_H8>.
Never emit POV tokens such as <PIECE_MN> or numbered squares such as <SQUARE_29>,
and never write moves in algebraic notation such as Nf3.

Every complete move is written as adjacent tokens. A non-capture has exactly
three tokens, <PIECE><FROM_SQUARE><TO_SQUARE>. A capture has exactly four,
<PIECE><FROM_SQUARE><CAPTURED_PIECE><TO_SQUARE>. A promotion appends the promoted
piece as a rare fifth token. Apply this convention both in prose and in any
structured fields."""

STYLE = """Preserve the established explanatory style and order. Begin with general
considerations and important features of the root position and its candidates.
Use later paragraphs for increasingly concrete plans, comparisons, tactics,
logic, and variations. Condense repeated motifs, but preserve decisive tactics
and forcing lines at full useful length. Emphasize the best candidate more than
inferior ones."""

FIVE_FIELDS = """Return exactly these five fields and no surrounding commentary:
ANALYSIS:
<fluent grounded root analysis>
BEST_MOVE: <one tokenized root move>
CRITICAL_LINE: <one tokenized root line>
PROMISING_MOVES: <one to four tokenized legal root candidates, best first>
EVALUATION: <one sentence with a pawn or mate evaluation from the root player's perspective>"""

PROSE_ONLY_FIELD = """Return exactly one field and no surrounding commentary:
ANALYSIS:
<fluent grounded root analysis>
Do not add BEST_MOVE, CRITICAL_LINE, PROMISING_MOVES or EVALUATION fields."""


def _position_block(fen: str, show_fen: bool) -> str:
    moves = ", ".join(legal_san(fen))
    if show_fen:
        return (f"Position (FEN): {fen}\nSide to move: {side_name(fen)}\n"
                f"Legal moves: {moves}")
    return (f"You are not shown the position. Side to move: {side_name(fen)}\n"
            f"Legal moves: {moves}")


# ------------------------------------------------------------ R′ chooser

CHOOSER_SYSTEM = """You are playing chess. Choose the best move for the side to move.
Any analysis you are given was produced by another chess model and may contain
mistakes. Reply with only a JSON object of the form
{"move": "<one legal move in SAN>", "reason": "<one or two sentences>"}."""


def chooser(fen: str, evidence: str | None, show_fen: bool = True) -> tuple[str, str]:
    user = _position_block(fen, show_fen)
    if evidence:
        user += f"\n\n{evidence}"
    return CHOOSER_SYSTEM, user


# --------------------------------------------------------------- reader

READER_SYSTEM = """You turn a chess model's written analysis into numbers a search
algorithm can use. Report what the analysis supports; where it is silent or
unclear, use your own judgement of the position. Reply with only a JSON object:
{"move_probs": {"<SAN>": <probability>, ...},
 "win_prob": <expected score for the side to move, 0 to 1>,
 "reason": "<one or two sentences>"}
List at most five legal moves in move_probs, most likely best first; the
probabilities are your belief that each move is the best move and need not sum
to 1."""


def reader(fen: str, evidence: str | None, show_fen: bool = True) -> tuple[str, str]:
    user = _position_block(fen, show_fen)
    user += f"\n\n{evidence}" if evidence else "\n\n(no analysis provided)"
    return READER_SYSTEM, user


def evidence_block(ranking: str | None = None, prose: str | None = None,
                   heads: str | None = None) -> str:
    """The rung's input, as a reader or chooser sees it."""
    parts = []
    if ranking is not None:
        parts.append("A chess model's written analysis of this position mentions "
                     f"these moves for the side to move, in order of first mention: {ranking}")
    if prose is not None:
        parts.append(f"A chess model's analysis of this position:\n<analysis>\n{prose}\n</analysis>")
    if heads is not None:
        parts.append(f"The chess model's conclusions:\n{heads}")
    return "\n\n".join(parts)


# -------------------------------------------------------- hybrid writer

HYBRID_SYSTEM = f"""You write the prose analysis of a chess position that explains
conclusions reached by a chess model. The conclusions (best move, critical line
and evaluation) are fixed: explain them, do not change, dispute or extend them,
and do not introduce other candidate moves as better. You may describe the
position's features and why the critical line goes as it does.

{STYLE}

{VOCABULARY}

{PROSE_ONLY_FIELD}"""


def hybrid_writer(fen: str, heads_human: str, heads_tokens: str,
                  target_words: int) -> tuple[str, str]:
    user = (
        f"ROOT FEN: {fen}\nSIDE TO MOVE: {side_name(fen)}\n\n"
        f"MODEL CONCLUSIONS (readable):\n{heads_human}\n\n"
        f"MODEL CONCLUSIONS (machine vocabulary):\n{heads_tokens}\n\n"
        f"Write about {target_words} words."
    )
    return HYBRID_SYSTEM, user


# --------------------------------------------------------- consolidator

_FULL_SELECTION = """The numerical selection rule supplied in the input is mandatory. Each
child's evaluation has been converted to the root player's expected score; BEST_MOVE
must be exactly the candidate marked MANDATORY BEST ROOT CANDIDATE, which has the
highest root expected score. Do not override this rule using the prose."""

_PROSE_SELECTION = """You are given only the children's prose, without their numerical
evaluations. Decide from the prose which root candidate is best for the root player,
make that judgement clear in the analysis, and keep it grounded in what the
children say."""


def _consolidator_system(variant: str) -> str:
    selection = _FULL_SELECTION if variant == "full" else _PROSE_SELECTION
    output = FIVE_FIELDS if variant == "full" else PROSE_ONLY_FIELD
    return f"""You are consolidating evaluations of the child positions of a
single root chess position. You are a faithful editor and synthesizer, not an
independent chess analyst. Every conclusion, positional claim, candidate, tactic,
and move sequence in your answer must be grounded in the supplied child
analyses. Do not add chess knowledge or repair their analysis yourself.

Each child position was reached by playing the labeled candidate from the root.
The analysis model then began afresh: its move numbers restart, and its side to
move is the root player's opponent, so every child analysis is written from the
OPPONENT'S perspective.

{selection}

In the consolidated text, restore the root player's point of view and restart
move numbering from the root. A continuation through a child must begin with the
labeled root candidate before the child's line.

{STYLE} The result is a root analysis, not a summary of separate positions.

{VOCABULARY}

{output}"""


def consolidator(fen: str, variant: str, children: list[dict],
                 target_words: int) -> tuple[str, str]:
    """``children``: dicts with uci, fen, text_abs (the child's text in absolute
    tokens: full generation for 'full', ANALYSIS only for 'prose'), and for
    'full' root_winrate. The mandatory candidate is the minimax best."""
    board = chess.Board(fen)
    blocks = []
    for label, child in zip("XYZ", children):
        lines = [f"CHILD {label}",
                 f"ROOT CANDIDATE: {absolute_move_tokens(board, chess.Move.from_uci(child['uci']))}",
                 f"CHILD FEN: {child['fen']}"]
        if variant == "full" and child.get("root_winrate") is not None:
            lines.append(f"ROOT PLAYER EXPECTED SCORE: {100 * child['root_winrate']:.1f}%")
        lines.append("CHILD ANALYSIS (opponent POV):")
        lines.append(child["text_abs"])
        blocks.append("\n".join(lines))
    head = f"ROOT FEN: {fen}\nROOT SIDE TO MOVE: {side_name(fen)}\n"
    if variant == "full":
        scored = [c for c in children if c.get("root_winrate") is not None]
        if scored:
            best = max(scored, key=lambda c: c["root_winrate"])
            head += ("MANDATORY BEST ROOT CANDIDATE: "
                     f"{absolute_move_tokens(board, chess.Move.from_uci(best['uci']))}\n")
    head += f"Write about {target_words} words of analysis.\n"
    return _consolidator_system(variant), head + "\n" + "\n\n".join(blocks)


def rewrite(fen: str, variant: str, text_abs: str, target_words: int) -> tuple[str, str]:
    """Depth-0 control: the consolidator rewrites the root analysis alone."""
    output = FIVE_FIELDS if variant == "full" else PROSE_ONLY_FIELD
    system = f"""You are editing a chess model's analysis of a position. You are a
faithful editor, not an independent chess analyst: keep every conclusion,
candidate, tactic and move sequence, and do not add chess knowledge or repair
the analysis yourself. Rewrite it as clear, fluent prose of about the same length.

{STYLE}

{VOCABULARY}

{output}"""
    user = (f"ROOT FEN: {fen}\nROOT SIDE TO MOVE: {side_name(fen)}\n"
            f"Write about {target_words} words of analysis.\n\n"
            f"ANALYSIS TO EDIT:\n{text_abs}")
    return system, user
