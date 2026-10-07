# Explanation-utility pilot

Purpose and design: `claude/AGENTS.md`, `claude/experiment_choices.md`.
Budget: $2k for the pilot; the API cap in `configs/explain/pilot.yaml` is $1.5k.

## Running it

Everything runs on the resolution-h200 cluster from a commit pushed to the
fork (`git@github.com:JacobPfau/queen.git`, branch `master`):

```bash
explain/cluster/launch.sh smoke        # 1 GPU: CUDA, Queen generation and reading, Qwen load
explain/cluster/launch.sh pilot [gpus] # default 4 GPUs: the whole pilot, then the report
explain/cluster/launch.sh report       # CPU only: re-score cached results, rewrite the report
```

- Keys: the `pfau-explain-env` Secret holds `ANTHROPIC_API_KEY` (Opus, Sonnet)
  and `OPENROUTER_API_KEY` (Gemini Flash), copied from Google Secret Manager.
- Storage: the shared `crusoe-fs` volume `pfau-explain-fs` at `/data` keeps
  results and caches; each pod downloads the Queen PAWN-8 and Qwen3.8-27B
  weights and builds its venv on its own disk (`/local`).
- The loop: each `advance` does every step whose inputs exist, then the GPU
  workers answer pending Queen and Qwen requests on every GPU. Every result is
  cached, so a relaunch resumes and never repeats GPU work or API spend. API
  spend stops at `max_api_spend_usd`.

## Queen as reader

Queen reads a text by pre-filling `ANALYSIS:\n<prose>\nBEST_MOVE:` and writing
the remaining head fields. The smoke test showed that pre-filling only the
ANALYSIS field lets Queen continue with an analysis of its own.

## Outputs

In `/data/work/pilot/` on the shared volume:

- `report.md`: model-substitution table (Flash and Sonnet against Opus, per
  role), writer vocabulary compliance, API and GPU cost, all cells.
- `samples.md`: texts and stated reasons for 10 positions, for reading.
- `decisions.jsonl`: one row per position and cell.
- `status_history.jsonl`: pending work and spend after every `advance`.

In `/data/runs/<job>/`: the pod's full log (`run.log`), `meta.json` (commit,
pod, node, GPUs), and each round's GPU worker logs.

`report.md` includes a health section that counts everything that can fail
quietly: API errors, refusals and cut-off outputs; Queen generations hitting
the token cap, unparseable fields and sign-ambiguous evaluations; writer
outputs Queen cannot read, length against target, and full consolidations whose
best move disagrees with the numeric minimax; and decision statuses by agent.
