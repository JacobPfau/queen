# Compute log

One entry per job submitted to the cluster, newest first, written when the job is submitted and updated with its outcome. Budgets: $2k for the pilot, $25k for the whole experiment (`claude/AGENTS.md`).

## pfau-explain-pilot-1007-195247

- **Job:** gpu queue, from JacobPfau/queen@5be342c, submitted 2026-10-07 19:52 UTC.
- **What it does:** runs the explanation-utility pilot end to end on 100 positions and writes the report.
- **Requests:** 1× H200, 16 CPU, 225Gi memory; storage `pfau-explain-pilot` (300Gi crusoe-ssd).
- **Expected runtime:** 3–5 h, done around 23:00–01:00 UTC; hard limit 48 h.
- **Expected cost:** ~5 GPU-h; API ~$500 (code cap $1,500; Flash draws on the OpenRouter key's $1k/week limit).
- **Budget so far:** ~$0.05 of $2k for the pilot (three test API calls).
- **Stop it:** `kubectl -n research delete job pfau-explain-pilot-1007-195247`
- **Cleanup:** the Job and its code ConfigMap are deleted 24 h after finishing; the PVC and results are kept.
- **Outcome:** running.

## Smoke tests, 2026-10-06 to 2026-10-07 (logged retroactively)

All five shared one shape: gpu queue, 1× H200, 16 CPU, 225Gi memory, PVC `pfau-explain-pilot`; no API keys and no API spend; hard limit 48 h; Job and ConfigMap deleted 24 h after finishing (failed ones were deleted by hand). Each checked CUDA, two Queen generations, one Queen read and the Qwen load. Times for the first three are approximate.

| Job | Commit | Ran | Outcome |
|---|---|---|---|
| pfau-explain-smoke-1007-002153 | 24bbc4c | 00:22–00:35 UTC | Passed; Queen read through `BEST_MOVE:` works |
| pfau-explain-smoke-1007-000936 | 8a7d6f0 | 00:10–00:21 UTC | Passed; Queen read kept writing its own analysis (fixed in 24bbc4c) |
| pfau-explain-smoke-1007-000509 | eb0777b | ~00:05–00:09 UTC | Failed: Triton found no C compiler (fixed in 8a7d6f0) |
| pfau-explain-smoke-1007-000110 | 2a09794 | ~00:01–00:04 UTC | Failed: venv's Python lost with the pod (fixed in eb0777b) |
| pfau-explain-smoke-1006-235527 | 150bc1d | ~23:55–00:00 UTC | Failed at the Stockfish download (404); models and environment were installed (fixed in 2a09794) |

Total for the smoke tests: about 1 GPU-hour, $0 API.
