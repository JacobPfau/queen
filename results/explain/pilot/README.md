# Explanation-utility pilot: results

## Summary

- **Flash can replace Opus in most roles.** It matches Opus to within about 1 point of regret everywhere, at about a quarter of the cost.
- **Except writing explanations.** When Flash writes prose, it adds factual chess errors. Keep Opus for that role.
- **Drop Sonnet.** It is about 2 points worse than both, which is outside the noise.
- **The LLMs rarely beat Queen on its own.** Picking directly, Opus given all of Queen's analysis lost 2.35 points; playing Queen's own best move lost 1.9. With a one-move search, the best LLM condition (1.17) only ties Queen's own evaluations (1.39) within noise.
- **Caveat:** one run, 100 positions. Single-cell differences under about 2 points are noise.

"Points" means regret: the win-rate percentage points lost compared with Stockfish's best move. Lower is better.

| Run | |
|---|---|
| Date | 2026-10-07 |
| Code | fork commit `f067dec` |
| API cost | $409.76 (Opus $319, Sonnet $58, Flash $32) |
| GPU | ~10 H200-hours, ~3 of them lost to failed jobs |
| Design and purpose | `claude/AGENTS.md`, `claude/experiment_choices.md` |
| Job log | `claude/compute_log.md` |

## Terms

| Term | Meaning |
|---|---|
| **Queen** | PAWN-8, the QUEEN paper's final chess model (arXiv 2610.03695). It writes prose analysis followed by structured conclusions. |
| **Queen's conclusions** | Its best move, critical line and evaluation (the structured fields after the prose). |
| **Input levels** | What a model is given from Queen: nothing; Queen's ranking of candidate moves; Queen's prose; Queen's conclusions; prose plus conclusions. |
| **Picks the move** | An LLM given the board and an input level answers with a move directly. No search. |
| **One-move search** | A reader judges each of the three positions reached by Queen's top three candidate moves; the search plays the move leading to the best-valued one. |
| **Reader** | An LLM that turns a text into move probabilities and a win estimate, which a search then uses. |
| **Consolidator** | Merges Queen's analyses of the three child positions into one root analysis. |
| **Hybrid prose** | Prose written by an LLM to explain Queen's conclusions (a control for whether Queen's own prose adds anything). |
| **Depth 0 / depth 1** | Reading Queen's analysis of the position itself, or a consolidation of its analyses one move ahead. |

## What ran

- **Positions:** 100 new positions from randomised Stockfish 19 self-play, taken at moves 8–35 where neither side was ahead by more than 3.5 pawns. No model can have memorised them.
- **Tree:** for each position, the root plus Queen's top three candidate moves.
- **Models:**

  | Role | Models |
  |---|---|
  | Consolidator | Qwen3.8-27B, Opus, Sonnet, Flash |
  | Hybrid-prose writer | Opus, Sonnet, Flash |
  | Reader | Queen, Opus, Sonnet, Flash |
  | Picks the move | Opus, Sonnet, Flash |

- **Extra conditions** for the move-pickers: without the board, and at low and high effort.
- **Scoring:** Stockfish 19 at 200k nodes per move. A failed answer (missing, refused, unparseable, illegal) is scored as a random legal move.

## How big is a difference?

**Reference points** (mean regret, points):

| Reference point | Regret |
|---|---|
| Random legal move | ≈27 (rough estimate) |
| Opus picking with no Queen input | 7.9 |
| Simple hand-crafted evaluation, one move deep | 5.0 |
| Playing Queen's best move directly | **1.9** |
| Queen's own evaluations, one move deep (best of 3 children) | **1.4** |
| Typical model conditions in this pilot | 1.5–5 |

**Noise:**

- **One condition, 100 positions:** the mean is uncertain by about ±1.3 points, and so is the difference between two models.
- **One role, all conditions pooled:** about ±0.5–0.7 points.
- **Heavy tail:** 55% of moves have zero regret; 7% lose more than 10 points. A few blunders drive the averages.
- **Sampling noise was not measured directly.** Effort settings shifted results by 1–3 points with no consistent direction, so treat gaps under ~2 points as noise.
- **Sample size for the main runs:** detecting a 0.5-point difference in one condition needs ~700 positions.

## Can Flash replace Opus?

**By regret** (Flash minus Opus; negative means Flash did better; 95% intervals):

| Role | Regret vs Opus | Same move | Cost per call (Opus → Flash) |
|---|---|---|---|
| Picks the move | −0.53 [−1.20, +0.16] | 75% | $0.018 → $0.008 (2.2× cheaper) |
| Reader, root text | −0.74 [−1.23, −0.31] | 90% | $0.015 → $0.002 (6.9×) |
| Reader, one-move search | +0.10 [−0.49, +0.66] | 72% | same as above |
| Consolidator | −0.15 | 93% | $0.112 → $0.018 (6.4×) |
| Hybrid-prose writer | −0.01 | 86% | $0.057 → $0.008 (7.4×) |

- **Overall cost:** Flash's calls would have cost **4.3×** as much on Opus. That's a quarter of the cost, not the hoped-for sixth.
- **Why picking moves saves less:** Flash thinks about 3× longer there (≈2,100 output tokens against 640).
- **Sonnet:** about 2 points worse as picker or reader, and 0.6 worse as consolidator. Drop it.

**By reading the outputs** (6 of the 10 sampled positions, checked against the board):

| Role | Verdict | Evidence |
|---|---|---|
| Hybrid-prose writer | **Keep Opus** | Flash claimed an extra pawn when material was level (2 positions), moved a knight onto its own bishop's square, got a square colour wrong, and raised moves it was told not to discuss. Opus counted material correctly; its one lapse was adding small plan suggestions. |
| Consolidator | Flash, with caveats | Same lines and verdicts as Opus in all six positions; errors only in side remarks. |
| Rewriting an analysis (control) | Flash, with caveats | Faithful, but ~13% longer than the source, and added one error. |
| Pickers' and readers' stated reasons | Flash, with caveats | Coherent and matched to its choice, but more tactical slips than Opus. |

- **Why the writer role matters despite equal regret:** hybrid prose is the control for "does Queen's prose carry information beyond its moves". Errors there change what the control measures, even if regret doesn't show it.
- **Keeping Opus there is cheap:** 4 calls per position.
- **All writers repeat Queen's own mistakes** faithfully (e.g. a phantom extra pawn).
- **Flash limits at scale:** OpenRouter allows 300 Flash requests per minute across all users; the key is capped at $1k per week; Flash's price doubles from 2027.

## Early findings on the experiment itself

Indicative only: one run, mostly within noise.

**1. Without search, each level of Queen input helped Opus pick better moves.**

Opus names a move in one call from the board plus Queen's analysis of the position itself:

| Opus is given | Regret |
|---|---|
| Nothing (board only) | 7.9 |
| Queen's move ranking | 5.1 |
| Queen's prose | 3.7 |
| Queen's conclusions | 2.6 |
| Prose + conclusions | 2.35 |

Most of the gain comes from the conclusions.

**2. With a one-move search, Queen's text helps more, and the gap to Queen narrows.**

A reader judges each child position (after one of Queen's top three moves) from the text below; the search plays the best child:

| Each child position is judged from | Opus | Flash | Queen as reader | No LLM |
|---|---|---|---|---|
| Board only (no Queen text) | 3.86 | 6.49 | – | – |
| Queen's prose | 3.63 | 2.22 | **1.43** | – |
| Queen's prose + conclusions | 1.76 | 1.45 | – | – |
| Hybrid prose (Opus-written) + conclusions | **1.17** | – | – | – |
| Queen's own evaluations (best of 3) | – | – | – | **1.39** |
| Hand-crafted evaluation | – | – | – | 3.58 |

- **Search helps once Queen's text is involved:** Opus with prose + conclusions goes from 2.35 (picking directly) to 1.76.
- **Best LLM result in the pilot:** Opus reading hybrid prose + conclusions, 1.17.
- **Part of the gain is Queen's shortlist:** the search only chooses among Queen's top three moves. The hand-crafted evaluation alone improves from 5.0 over all moves to 3.58 over those three.
- **Hiding the board helps here too:** Opus judging from Queen's prose goes from 3.63 to 2.19 without the board.

**3. The LLMs rarely improved on Queen alone.**
- Without search, Opus with everything: 2.35. Queen's best move played directly: 1.9.
- With search, Queen reading its own prose (1.43) and Queen's own evaluations (1.39) match or beat every LLM condition except Opus on hybrid prose (1.17), and that gap is within noise.
- A third mode, a reader reporting which move Queen's root analysis supports (no search): Opus scores 2.29 from prose and 1.90 from prose + conclusions, the same as Queen's own best move, because it passes Queen's choice through.
- So far the LLMs add noise to Queen's choices about as often as they fix them. This is the main thing the full experiment has to explain.

**4. Reading a consolidation of one move ahead helped.**
- Opus picking from a depth-1 consolidation: 1.45–2.45 (depending on the consolidator), against 2.35 at depth 0.
- Queen's own evaluations one move deep: 1.4, the best result in the pilot.
- A rewrite of the depth-0 analysis alone scored 1.9–2.9, so the gain comes from the extra analysis, not from the editing.

**5. Hiding the board often helped.**
- Without the board, models deferred to Queen more.
- Picking directly: Opus with Queen's prose 3.68 → 2.90; Opus with Queen's conclusions 2.57 → 1.90; Sonnet with Queen's conclusions 4.86 → 2.33.
- With search: Opus judging from Queen's prose 3.63 → 2.19.
- The current decision is to always show the board, so this is flagged for review.

**6. Higher effort didn't reliably help** any model.

## Problems found and fixed

The pilot doubled as a debugging run. Each problem was caught by its health counts or logs.

| Problem | Effect | Fix (commit) |
|---|---|---|
| **Queen's evaluations misread.** It writes "the player is up/down X pawns"; the shared parser read the number as White's view. | Sign right only at chance (27/46). Contaminated every input that used Queen's evaluations. | Direction-aware parser: 63/67 signs now match Stockfish, against 46/67 (`f067dec`) |
| **Qwen ran out of tokens** while thinking (26% of consolidations). | The cut-off thinking was read as if it were prose. | 24k-token budget, cut-off outputs regenerated, outputs without an analysis rejected (`edfd3ef`) |
| Consolidation without parseable conclusions | Pipeline crash | Require parsed conclusions (`edfd3ef`) |
| Flash rate limit (300 requests per minute) | 119 calls refused | Lower concurrency, exponential backoff (`edfd3ef`) |
| Cluster disk tried to reformat after moving node | Job stuck 33 min holding 4 GPUs | Shared network volume; watcher checks pod state (`5ca73a9`) |
| Setup script died on a broken pipe | Job failed at setup | Fixed the version check (`bf08815`) |
| Queen as reader kept writing its own analysis | Reads ignored the given text | Pre-fill through the best-move field (`24bbc4c`) |

**Health of the final run:**
- Failed answers: under 0.5% for every model.
- API: no errors; 7 Opus refusals in 6,412 move-picking calls.
- Queen: no output hit its length limit, and it supplied all 3 candidate moves in every position.
- Writers: 97–100% of outputs usable.
- Full consolidations: the best move matched Queen's evaluations 392 of 392 times.

## Proposed changes for the main runs

**Need your decision:**
- **Model roles:** Flash for reading, picking and consolidating; Opus for hybrid prose; Sonnet dropped.
- **The board:** keep always showing it, or revisit in light of finding 5.

**Ready to do:**
- **Writer prompt:** tighten it so writers stop adding plans and evaluative language.
- **Queen-alone reference:** add "play Queen's best move" and "Queen's evaluations one move deep" as reference points in every comparison.
- **Measured noise:** re-run ~20 positions with new seeds.
- **Sample size:** size positions for the effects that matter (~700 for 0.5 points in one condition).
- **Flash limits:** plan throughput around 300 requests per minute and $1k per week.

## Files

| File | Contents |
|---|---|
| `report.md` | Generated report: every condition, model comparisons, health counts, costs |
| `report.json` | The same, machine-readable |
| `samples.md.gz` | Texts and stated reasons for 10 positions |
| `status_history.jsonl` | Pending work and spend after each pipeline step |
| Cluster volume `pfau-explain-fs`, `/data/work/pilot/` | Per-decision data (9 MB) and all model outputs |
