# Explanation-utility pilot: results

The pilot's two outcomes are a role assignment and a warning about the experiment's design. Gemini 3.8 Flash matches Claude Opus 5.5 to within about 1 percentage point of regret in every role, at about a quarter of the cost, but it adds factual errors when it writes explanatory prose. The proposed assignment is therefore Flash for reading, choosing and consolidating, and Opus for writing hybrid prose; this is a proposal, not yet a decision. The warning is that external LLMs rarely improved on Queen's own outputs: Opus given all of Queen's analysis lost more win rate (2.35 pp) than simply playing Queen's best move (1.9 pp).

These are results from one run over 100 positions. Differences under about 2 pp in a single cell are within noise (see "Scale and noise"), so the findings below are indicative.

Run: 2026-10-07, fork commit `f067dec`, $409.76 of API calls (Opus $318.93, Sonnet $58.46, Flash $32.37) and about 10 GPU-hours on H200s, of which about 3 were lost to failed jobs (`claude/compute_log.md`). Design and purpose: `claude/AGENTS.md`, `claude/experiment_choices.md`.

## What ran

- **Positions:** 100, from Stockfish 19 self-play with randomised move choice, taken at plies 16–70 where Stockfish's evaluation was within ±3.5 pawns. They are new positions, so no model can have memorised them.
- **Queen:** PAWN-8, the paper's final model (arXiv 2610.03695), with its release prompt and sampling settings.
- **Tree:** one shared depth-1 tree per position: the root plus Queen's top three candidate moves. Each rung was evaluated at depth 0 (the root analysis), at depth 1 (a consolidation of the three children's analyses), and by a one-ply search over the children.
- **Roles:** consolidators (Qwen3.8-27B, Opus, Sonnet, Flash) in prose-only and full variants; hybrid-prose writers (Opus, Sonnet, Flash); readers (Queen, Opus, Sonnet, Flash); and models choosing a move directly (the R′ arm, Opus, Sonnet, Flash), including runs without the board and at low and high effort.
- **Scoring:** each chosen move's Stockfish 19 win rate (200k nodes per move) is subtracted from the best move's, giving regret in percentage points (pp). A decision that failed (missing, refused, unparseable, illegal or empty) is scored as a uniformly random legal move.

## Scale and noise

Mean regret per decision:

| Reference point | Regret (pp) |
|---|---|
| Uniform random legal move | ≈27 (estimated from only 45 failed decisions) |
| Opus choosing with no Queen input (R0′) | 7.9 |
| Hand-crafted evaluation, one-ply search over all moves (R0) | 5.0 |
| Playing Queen's own BEST_MOVE (R3, no LLM) | 1.9 |
| Queen's numeric minimax over its three children (R3, depth 1) | 1.4 |
| Typical reader and chooser cells | 1.5–5 |

The noise comes from three sources:

- **Sample size.** One cell's mean has a 95% interval of about ±1.3 pp at 100 positions, and so does a paired difference between two models in the same cell. Pooled over a role's cells, intervals narrow to about ±0.5–0.7 pp.
- **The shape of regret.** 55% of decisions have zero regret, 7% exceed 10 pp and 2% exceed 30 pp, so a few blunders drive the means. The per-position difference between two models has a standard deviation of 2.4–3.5 pp.
- **Sampling.** This was not measured, because no input was run twice. The nearest proxy is the same model and prompt at different effort levels: cells move by 1–3 pp with no consistent direction (Opus with no Queen input scored 9.4 at low effort, 7.9 at medium, 6.5 at high).

Interval half-width shrinks with the square root of the number of positions, so detecting a 0.5 pp difference in a single cell would take roughly 700 positions.

## Can Flash replace Opus?

On regret, Flash matches Opus in every role. The values below are Flash minus Opus over the same positions and cells (negative means Flash did better), with 95% intervals:

| Role | Regret vs Opus (pp) | Same move as Opus | Cost per call, Opus vs Flash |
|---|---|---|---|
| Chooser (R′) | −0.53 [−1.20, +0.16] | 75% | $0.0181 vs $0.0084 (2.2× cheaper) |
| Reader, root texts | −0.74 [−1.23, −0.31] | 90% | $0.0146 vs $0.0021 (6.9×) |
| Reader, one-ply search | +0.10 [−0.49, +0.66] | 72% | as above |
| Consolidator | −0.15 | 93% | $0.112 vs $0.018 (6.4×) |
| Rewrite control | not measured separately | – | $0.057 vs $0.013 (4.4×) |
| Hybrid writer | −0.01 | 86% | $0.057 vs $0.008 (7.4×) |

Across all of Flash's calls, the same calls on Opus would have cost 4.3 times as much: about a quarter of the cost, not the hoped-for sixth. Choosing is the reason. When it chooses a move, Flash writes about 2,100 output tokens (mostly thinking) against Opus's 640, so its per-call saving there is only 2.2×. Sonnet is worse than both on regret, by about 2 pp as a chooser or reader and 0.6 pp as a consolidator, which is outside the noise. It should not take any role.

The written outputs tell a different story for one role. A read of 6 of the 10 sampled positions, comparing each model's texts against the board, gave these verdicts:

- **Hybrid writer: keep Opus.** Flash added errors to texts that readers depend on. It stated an extra pawn where material was level (p0008, p0015), described a knight move onto a square its own bishop occupied (p0072), and gave a square colour wrong (p0015). It also raised alternatives it had been told not to discuss, and overstated evaluations ("smoothly winning" for a 66% expected score, p0032). Opus counted material correctly and stayed concrete. Its own lapse was adding small plan suggestions, which bends the instruction not to extend Queen's conclusions. The hybrid arm is the control for whether Queen's prose carries information beyond its moves, so errors that regret does not register still change what that control measures. Hybrid writing is 4 calls per position, so keeping Opus here costs little.
- **Consolidator: Flash, with caveats.** In all six positions Flash followed the same child lines and verdict as Opus and stayed grounded in the children. Its errors were in explanatory asides, for example misattributing which piece controls f6 (p0015).
- **Rewrite control: Flash, with caveats.** Flash's rewrites were faithful but ran longer than the source (about 600 words against 530) and added one error (p0032).
- **Chooser and reader rationales: Flash, with caveats.** Flash's stated reasons were coherent and matched its choices, but contained more tactical slips than Opus's, such as a recapture by a knight that could not reach the square (p0017).

All writers passed on Queen's own errors faithfully. For example, Queen claimed an extra pawn in p0097 and p0015 where material was level. Sonnet's hybrids had the most chess errors of any writer.

Two limits apply to Flash at scale. OpenRouter caps `gemini-3.8-flash` at 300 requests per minute across all its users, and the OpenRouter key has a $1k weekly spend limit. Flash's promotional price also doubles from 2027.

## Early findings on the experiment itself

These come from a single run on 100 positions, and most single-cell differences are within noise. They are listed to shape the main runs, not as conclusions.

- **Each rung of Queen input helped the Opus chooser.** Its regret fell from 7.9 pp with nothing (R0′) to 5.1 with the ranking extracted from the prose (R1′), 3.7 with the full prose (R2′), 2.6 with the heads (R3′) and 2.35 with prose plus heads (R4′). The heads carried most of the gain.
- **External models rarely improved on Queen alone.** Opus with prose and heads (2.35 pp) did worse than playing Queen's BEST_MOVE directly (1.9 pp). So far the LLMs add noise to Queen's choices more often than they correct them. That is the main thing the full experiment needs to explain. It also argues for playing Queen's heads directly as a reference point in every comparison.
- **Depth 1 helped.** Opus reading full depth-1 consolidations scored 1.45–2.45 pp (by consolidator) against 2.35 at depth 0. Queen's numeric minimax over the three children scored 1.4 pp, the best result in the run. The depth-0 rewrite controls (1.9–2.9 pp) were closer to depth 0 than to depth 1, so most of the depth-1 gain comes from the children's analyses rather than from the editor's rewording.
- **Hiding the board often helped.** Without the FEN, models followed Queen more and overrode it less. With prose only (R2′), Opus went from 3.68 pp to 2.90. With heads (R3′), Opus went from 2.57 to 1.90 and Sonnet from 4.86 to 2.33. The owner's decision is that models always see the board, so this is flagged for review rather than acted on.
- **Higher effort did not help reliably.** No model improved consistently across effort levels.

## Problems the pilot found and fixed

The pilot was also a debugging run. Each problem below was caught by its health counts or logs and fixed before the final run, in the fork commit shown.

| Problem | Effect | Fix |
|---|---|---|
| Queen's evaluations misread. PAWN-8 writes "the player is up/down X pawns", and the shared parser fell back to reading the number from White's side. | The parsed sign agreed with Stockfish at chance (27/46 clear positions). This contaminated R3/R4 prompts, Queen-reader values, one-ply values and full consolidations. | A direction-aware parser: 63/67 clear roots now agree with Stockfish, against 46/67 before. The report tracks sign agreement in every run (`f067dec`). |
| 26% of Qwen consolidations (254/974) were cut off at 8,192 tokens while still thinking. | The cut-off thinking was parsed as prose, so some reader calls read Qwen's thinking instead of a consolidation. | 24k output tokens; cut-off outputs regenerated; a writer output without an `ANALYSIS` field is now a failure (`edfd3ef`). |
| A full consolidation without parseable heads. | The pipeline crashed at the start of round 4. | R3/R4 cells require parsed heads (`edfd3ef`). |
| OpenRouter rate limit on Flash (300 requests/min). | 119 Flash calls were refused. | Flash concurrency cut to 32, plus exponential backoff (`edfd3ef`). |
| A crusoe-ssd volume tried to reformat on mount after moving node. | One job sat 33 min holding 4 GPUs. | A shared crusoe-fs volume; the watcher now checks pod phase (`5ca73a9`). |
| Setup's Stockfish check died of SIGPIPE under `pipefail`. | One job failed at the end of setup. | Capture the output, then grep it (`bf08815`). |
| Queen-as-reader pre-filled only `ANALYSIS:`. | Queen wrote its own analysis instead of reading the given one. | Pre-fill through `BEST_MOVE:` (`24bbc4c`). |

Health of the final run:

- **Failures:** decision failures were under 0.5% for every model. No API errors; 7 Opus refusals among 6,412 chooser calls.
- **Queen:** no analysis hit its token cap, and Queen supplied all three of the tree's children in every position.
- **Writers:** 97–100% of writer outputs were readable by Queen (Qwen lowest at 97.5%; Sonnet had 7 vocabulary failures out of 800). Full consolidations' best moves matched the numeric minimax in 392 of 392 cases.

## Proposed changes for the main runs

- **Role assignment:** Flash as reader, chooser, consolidator and rewriter; Opus as hybrid writer; Sonnet dropped. This is pending the owner's confirmation.
- **Hybrid-writer prompt:** tighten it, so writers stop adding plans and evaluative language.
- **Queen-alone reference:** add Queen's BEST_MOVE and its numeric minimax as explicit reference points in every comparison.
- **Measured noise:** re-run about 20 positions with new seeds, so sampling noise is measured instead of inferred from effort variants.
- **Positions:** size the position set for the effects that matter. About 700 positions would be needed to detect 0.5 pp in a single cell.
- **Flash throughput:** plan around OpenRouter's 300 requests/min and the key's $1k weekly limit.
- **The no-FEN finding:** revisit the always-show-the-board decision in light of it.

## Files

- `report.md`: generated report with every cell, the model-substitution tables, health counts and costs.
- `report.json`: the same data in machine-readable form.
- `samples.md.gz`: texts and stated reasons for 10 positions, used for the reading above.
- `status_history.jsonl`: pending work and spend after every pipeline step of the final run.
- Per-decision data (`decisions.jsonl`, 9 MB) and all model outputs remain on the cluster volume `pfau-explain-fs` under `/data/work/pilot/`.
