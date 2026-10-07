# Compute log

One entry per job submitted to the cluster, newest first, written when the job is submitted and updated with its outcome. Budgets: $2k for the pilot, $25k for the whole experiment (`claude/AGENTS.md`).

## pfau-explain-pilot-1007-203643

- **Job:** gpu queue, from JacobPfau/queen@5ca73a9, submitted 2026-10-07 20:36 UTC.
- **What it does:** runs the pilot end to end on 100 positions as a debugging run (health counts, persistent run logs in `/data/runs/<job>`), with Queen and Qwen requests split across 4 GPUs.
- **Requests:** 4× H200, 64 CPU, 900Gi memory; storage `pfau-explain-fs` (1Ti crusoe-fs, new); models and venv on the pod's own disk.
- **Expected runtime:** 1.5–2.5 h including ~15 min of downloads, done around 22:00–23:00 UTC; hard limit 48 h.
- **Expected cost:** ~6–10 GPU-h; API ~$500 (code cap $1,500; Flash draws on the OpenRouter key's $1k/week limit).
- **Budget so far:** ~$0.05 of $2k for the pilot, plus ~2.5 GPU-h lost to the stuck job below.
- **Stop it:** `kubectl -n research delete job pfau-explain-pilot-1007-203643`
- **Cleanup:** the Job and its code ConfigMap are deleted 24 h after finishing; the shared PVC and results are kept.
- **Outcome:** running.

## pfau-explain-pilot-1007-200151

- **Job:** gpu queue, from JacobPfau/queen@5b51f38, submitted 2026-10-07 20:01 UTC.
- **What it does:** runs the explanation-utility pilot end to end on 100 positions and writes the report; Queen and Qwen requests are split across 4 GPUs, one worker per GPU.
- **Requests:** 4× H200, 64 CPU, 900Gi memory; storage `pfau-explain-pilot` (300Gi crusoe-ssd).
- **Expected runtime:** 1–2 h, done around 21:00–22:00 UTC; hard limit 48 h.
- **Expected cost:** ~5 GPU-h (4 GPUs, mostly idle during API rounds); API ~$500 (code cap $1,500; Flash draws on the OpenRouter key's $1k/week limit).
- **Budget so far:** ~$0.05 of $2k for the pilot.
- **Stop it:** `kubectl -n research delete job pfau-explain-pilot-1007-200151`
- **Cleanup:** the Job and its code ConfigMap are deleted 24 h after finishing; the PVC and results are kept.
- **Outcome:** never started. Its pod sat in ContainerCreating for ~33 min (20:01–20:34 UTC) because mounting the crusoe-ssd PVC on a new node failed: the driver tried to reformat the disk (`mke2fs` failed). Deleted by hand; no API spend, but 4 GPUs were held, ~2.2 GPU-h. Replaced by a crusoe-fs volume.

## pfau-explain-pilot-1007-200046

- **Job:** gpu queue, from JacobPfau/queen@7b269e8, submitted 2026-10-07 20:00 UTC.
- **What it does:** runs the explanation-utility pilot end to end on 100 positions and writes the report; same as the job below, with per-model API concurrency (Opus and Sonnet 128, Flash 64) and Qwen batches of 64.
- **Requests:** 1× H200, 16 CPU, 225Gi memory; storage `pfau-explain-pilot` (300Gi crusoe-ssd).
- **Expected runtime:** 1.5–3 h, done around 21:30–23:00 UTC; hard limit 48 h.
- **Expected cost:** ~3 GPU-h; API ~$500 (code cap $1,500; Flash draws on the OpenRouter key's $1k/week limit).
- **Budget so far:** ~$0.05 of $2k for the pilot.
- **Stop it:** `kubectl -n research delete job pfau-explain-pilot-1007-200046`
- **Cleanup:** the Job and its code ConfigMap are deleted 24 h after finishing; the PVC and results are kept.
- **Outcome:** stopped by hand at 20:01 UTC during setup, to relaunch on 4 GPUs; no API spend, under 0.05 GPU-h.

## pfau-explain-pilot-1007-195247

- **Job:** gpu queue, from JacobPfau/queen@5be342c, submitted 2026-10-07 19:52 UTC.
- **What it does:** runs the explanation-utility pilot end to end on 100 positions and writes the report.
- **Requests:** 1× H200, 16 CPU, 225Gi memory; storage `pfau-explain-pilot` (300Gi crusoe-ssd).
- **Expected runtime:** 3–5 h, done around 23:00–01:00 UTC; hard limit 48 h.
- **Expected cost:** ~5 GPU-h; API ~$500 (code cap $1,500; Flash draws on the OpenRouter key's $1k/week limit).
- **Budget so far:** ~$0.05 of $2k for the pilot (three test API calls).
- **Stop it:** `kubectl -n research delete job pfau-explain-pilot-1007-195247`
- **Cleanup:** the Job and its code ConfigMap are deleted 24 h after finishing; the PVC and results are kept.
- **Outcome:** stopped by hand at 20:00 UTC, while it was still sampling positions, to relaunch with higher API concurrency; no API spend, about 0.1 GPU-h.

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
