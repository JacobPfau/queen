# Explanation-utility experiment: design choices

Log of design choices for testing whether Queen's explanations help inference-time search. Choices are grouped by who made them: **Decided by the owner**, or **Decided by Claude's judgment**, which the owner asked Claude to settle in line with the owner's decisions and may override. Started 2026-10-06. The purpose of the experiment is stated in `claude/AGENTS.md`, and the judgment calls below favour whichever option keeps the explanations' contribution separable.

## Decided by the owner

- **Queen is the paper's final model, PAWN-8.** The owner asked for the best available Queen; the paper (arXiv 2610.03695) names PAWN-8 as the final model at 2697 Elo, while the other release, HCE-4, is its handcrafted-evaluation ablation. Queen runs with its release's own prompt and sampling settings (temperature 0.6, top-k 20, top-p 0.95).
- **Five-rung input ladder (R0–R4).** The search receives nothing (R0), the candidate-move ranking extracted from the prose (R1), the full prose (R2), Queen's structured heads, meaning best move, PV and eval (R3), or prose plus heads (R4). The heads are the `BEST_MOVE`, `CRITICAL_LINE` and `EVALUATION` text fields that Queen writes after `ANALYSIS`, not separate network heads.
- **Two readers: Queen and Opus 5.5.** A reader turns prose into a move prior and a value the search can use. Comparing the two on the same text separates what the prose contains from how well a given model can extract it.
- **Opus ladder (R0′–R4′).** Opus 5.5 receives the same five input levels as the search, with R0′ measuring Opus's chess ability without any Queen output. The R′ arm asks whether Queen's outputs help a frontier model, beyond helping a search.
- **Hybrid prose.** Opus is given the moves Queen suggests and writes its own prose, which then goes through the prose-bearing rungs. If hybrid prose does as well as Queen's prose, Queen's prose carries no useful information beyond its moves.
- **Depth as a fourth axis.** Depth is the amount of analysis from downstream positions that is backed up into the root text. It tests whether analysing child positions and passing the results back up adds information beyond Queen's single-position analysis.
- **NL MCTS with a fixed-length backup.** Each node holds one natural-language analysis, and the backup step rewrites a parent's analysis from its children's analyses at roughly the length of one analysis. Without this cap, context length would grow with depth and be confounded with the information depth adds.
- **Strict channel ablation.** A rung's channel restriction applies at every node, so for R1 and R2 the consolidator sees only the children's `ANALYSIS` fields and no numeric heads. If the consolidator saw child evals, backed-up "prose-only" text would carry head information and R2 and R3 would converge with depth.
- **Minimax backup.** The parent's best move and value come from the best child, not a visit-weighted average. The existing consolidation recipe already uses this rule (lowest opponent eval wins), so the root text states one best line with a definite value.
- **Consolidator: Qwen, with Opus as a separate arm.** The main runs use the existing Qwen3.8-27B "faithful editor" recipe from `datagen/self_distill/consolidation.py`, and Opus-as-consolidator is a separate arm. Holding the consolidator fixed within an arm prevents a stronger editor from adding its own chess knowledge in some cells and not others.
- **NL selection for the prose-based rungs.** In R1, R2 and R4, the search chooses which nodes to expand from each node's current natural-language analysis, read by the rung's reader, rather than from numeric evaluations. This requires NL backups during search instead of a single pass after the tree is fixed, since selection must read backed-up text.
- **No Stockfish truncation in consolidation.** The training recipe cuts child lines at the first Stockfish-100k mistake (`BOUNDARY_INSTRUCTIONS`), which would leak the oracle into every condition at test time. Only legality truncation is allowed, and the prompt sections that refer to Stockfish boundaries are rewritten.
- **Every model gets the game state.** Readers, consolidators, hybrid-prose writers and the R′ arm all receive the FEN. A small pilot without the FEN will be run, with the owner's expectation that it lowers performance.
- **Pilot across three external LLMs.** The pilot runs Opus 5.5, Sonnet 5.5 and Gemini 3.8 Flash (or the latest Flash model). Its design is set under "Pilot" below.

## Decided by Claude's judgment

### Generation and inputs

- **One Queen generation per position, shared across rungs.** Queen's output for each position is generated once, cached, and shown to each rung as a different view. Every rung then reads the same sample, so differences between rungs come from the channel and not from sampling noise.
- **Queen sampling matches the Elo ladder.** Queen generates at temperature 0.6, top-k 20, top-p 0.95, with the seed derived from the position so reruns are deterministic. These are the settings `configs/eval/model_ladder.yaml` uses, so results line up with Queen's existing evaluations.
- **External LLMs read SAN, with the translation audited.** Queen's board-relative move tokens are translated to SAN with `utils/translate_helpers.Translator` before any external model reads them, and 200 translated analyses are checked against the board. A translation error would otherwise show up as a reader failing to understand the prose.
- **External LLM responses are cached and run through the Batch API.** Every response is stored keyed by model, prompt and position, so reruns and new analyses never re-query. Batch pricing halves the API cost, and none of the calls are latency-sensitive.

### Rungs and arms

- **R0′–R4′ means the external LLM picks the move directly.** The model receives the FEN plus the rung's Queen outputs and returns one move, with one call per position and no search. This is the cleanest test of whether Queen's outputs help a frontier model, and an LLM inside the search is already covered by the reader arm.
- **Hybrid prose is written from Queen's heads plus the FEN.** The writer receives `BEST_MOVE`, `CRITICAL_LINE` and `EVALUATION` but not Queen's prose, and is instructed to explain those conclusions without changing them, as the consolidator's "faithful editor" prompt does. The hybrid then carries the same move and value information as R3, so hybrid-versus-Queen prose compares explanations of the same conclusions.
- **Hybrid prose is written at every node, to depth 2, on 2k positions.** Writing it only at the root would compare a backed-up Queen tree with a single rewrite, which mixes depth with authorship. Depth 3 needs 40 writes per position and adds little over depth 2 for this comparison, so it is skipped.
- **The Opus reader runs in the one-ply search only.** Opus reads the root and the top 8 children, and the full MCTS uses Queen as the reader. Opus calls at every MCTS node would cost hundreds of thousands of dollars, and the one-ply search is enough to compare readers on the same texts.
- **External LLM effort is fixed at medium.** Medium is Opus 5.5's default and keeps R0′ below its ceiling, which leaves room to measure what Queen adds. The pilot measures low and high effort on R0′ and R4′, and the main runs change level only if medium turns out clearly unrepresentative.

### Search

- **Fixed-width trees for the depth axis.** Depth runs expand k = 3 children per node at d ∈ {0, 1, 2, 3}, matching the existing three-child consolidation. Each rung chooses its three children with its own prior, so the prose-based rungs choose from the node's text, as NL selection requires.
- **A shared-tree control at depth 1 and 2, on 1k positions.** Alongside the rung-specific trees, every rung also reads a tree whose children were chosen by R3's numeric prior. Comparing the two splits a prose rung's gain into a better choice of children and better reading of the backed-up text.
- **NL backups after each batch of 16 leaves.** The search expands 16 leaves at a time using virtual loss, then re-consolidates every node whose subtree changed before the next selection. Batching only merges consolidations of shared ancestors, so it saves about 1.8× rather than 16×: roughly 720 consolidations per 256-node tree against 1,280 when backing up after every simulation. The batch size is the same for every rung.
- **MCTS budgets of 1, 4, 16, 64 and 256 nodes.** Each run goes to 256 nodes and records its move choice at each smaller budget, so one run yields the whole curve. Budget 1 with the R3 view reproduces the current ladder's move choice, which serves as a sanity check.
- **Base evaluator: HCE plus quiescence search.** R0, and R1's value, fall back on the repo's hand-crafted evaluation with a capture-only search. Stockfish would be strong enough to hide any contribution from Queen.
- **Equal tuning budget per rung.** Each rung gets the same hyperparameter grid (prior weight, value-mix weight, PUCT exploration constant, prior temperature) on the development set, and settings are then frozen. Unequal tuning would make a rung look better for reasons unrelated to its input.

### Consolidation and context

- **Per-node length cap at Queen's 90th-percentile analysis length.** The cap is measured on the development set, so backed-up text stays within the length range Queen produces and reads. A cap well above Queen's usual length would put Queen-as-reader out of distribution.
- **Queen's context raised to 4096 tokens for reading.** The default `max_model_len=2048` cannot hold the prompt, a capped analysis and the decoded heads together. Native evaluation already runs Queen with up to 8192 new tokens (`configs/eval/analysis.yaml`), so 4096 is within what it has handled.
- **Two consolidation controls.** A depth-0 rewrite, in which the consolidator rewrites the root analysis alone, isolates any gain from the editor's rewording. A depth-1 uncompressed control, giving the reader the root plus all three child analyses concatenated, measures what compression loses.

### Positions and metrics

- **1k development and 5k test positions, with costly arms on a 2k subset.** Depth 3, the Opus consolidator arm, hybrid prose and the Opus reader run on a fixed 2k subset of the test set. Using the same subset for all of them keeps their comparisons paired.
- **Contamination-free positions.** Test positions come from games played after the external LLMs' training cutoffs or from engine play, and exclude Queen's self-distill positions. The external models may have memorised well-known Lichess puzzles, which would inflate R0′.
- **Primary metric: win-rate regret against Stockfish.** Each chosen move is scored by `ParallelOracle` as the win-rate drop from Stockfish's best move, with paired bootstrap intervals over positions. Top-1 agreement and puzzle solve rate are secondary.
- **Failed decisions are scored as a uniformly random move, and every failure rate is reported.** The owner set this rule: a cell whose answer is missing, refused, unparseable, illegal or empty is scored at the expected regret of a uniformly random legal move, and the report gives each cell's failure rate and its regret over successes alone. The report also gives the share of one-ply children whose reading failed, the share of Queen reads truncated, and how many of the shared tree's children Queen itself supplied.
- **Elo only for the 3–4 best cells.** A numeric-rung Elo target costs about 11 H100-hours at 64 nodes per move, but a prose-based rung needs NL backups at every move and costs about 200, and regret on fixed positions already ranks the cells. Elo checks that the ranking holds in full games.
- **Results reported against both node count and cost.** An external LLM call costs far more than a Queen node, so matching on node count favours the LLM and matching on cost favours Queen. Plots show both.

### Pilot

- **Pilot on 100 development positions, through the full pipeline.** It runs every arm at depth 0 and 1 with Opus 5.5, Sonnet 5.5 and Gemini 3.8 Flash (or the latest Flash) in each external-LLM role. It replaces the compute estimate's assumptions with measured token counts and throughput before the main runs are sized.
- **The pilot uses only the shared tree, with a one-ply search over its three children.** Children are Queen's top three moves by its numeric prior, so the pilot does not test NL selection; rung-specific trees and NL MCTS start with the main runs. This keeps the pilot cheap while still measuring every role's cost, readability and accuracy.
- **Flash is judged against Opus by paired regret and by reading.** Each Flash cell is compared with the identical Opus cell on the same positions (regret difference with a bootstrap interval, and how often both pick the same move), and a sample of Flash's written outputs is read for chess sense and faithfulness. Flash replaces Opus in a role only if both checks pass at roughly a sixth of the cost.
- **The pilot also covers the no-FEN, effort and model checks.** It runs a no-FEN version of the reader and R′ arms, low/medium/high effort on R0′ and R4′, and compares the three models in each role. The main runs then keep Opus 5.5 in the roles the owner assigned it and use the pilot to decide whether the cheaper models can take the high-volume roles (hybrid writing, the one-ply reader sweep) without changing the results.
