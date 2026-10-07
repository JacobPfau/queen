# Compute log

One entry per job submitted to the cluster, newest first, written when the job is submitted and updated with its outcome. Budgets: $2k for the pilot, $25k for the whole experiment (`claude/AGENTS.md`).

## pfau-explain-pilot-1007-222925

- **Job:** gpu queue, from JacobPfau/queen@f067dec, submitted 2026-10-07 22:29 UTC.
- **What it does:** resumes the pilot from its cache with Queen's evaluations read by the direction-aware parser; redoes only work whose inputs changed (R3/R4 prompts, Queen-reader values, full consolidations and what depends on them).
- **Requests:** 4× H200, 64 CPU, 900Gi memory; storage `pfau-explain-fs` (1Ti crusoe-fs); models and venv on the pod's own disk.
- **Expected runtime:** 30–60 min, done around 23:00–23:30 UTC; hard limit 48 h.
- **Expected cost:** ~3 GPU-h; API ~$50–150 more (code cap $1,500).
- **Budget so far:** $343 API of $2k for the pilot, plus ~8 GPU-h.
- **Stop it:** `kubectl -n research delete job pfau-explain-pilot-1007-222925`
- **Cleanup:** the Job and its code ConfigMap are deleted 24 h after finishing; the shared PVC and results are kept.
- **Outcome:** succeeded at 22:59 UTC (30 min). Redid the work affected by the parser fix; no API failures. Pilot totals: $409.76 API (Opus $319, Sonnet $58, Flash $32) and ~10 GPU-h, of which ~3 were lost to failed jobs. Report in `results/explain/pilot/`.

## pfau-explain-pilot-1007-215037

- **Job:** gpu queue, from JacobPfau/queen@edfd3ef, submitted 2026-10-07 21:50 UTC.
- **What it does:** resumes the debugging pilot from its cache, with the round-4 crash fixed, Qwen allowed 24k output tokens (cut-off consolidations redone), and Flash held under OpenRouter's 300 requests/min.
- **Requests:** 4× H200, 64 CPU, 900Gi memory; storage `pfau-explain-fs` (1Ti crusoe-fs); models and venv on the pod's own disk.
- **Expected runtime:** 1–1.5 h, done around 23:00–23:30 UTC; hard limit 48 h.
- **Expected cost:** ~5 GPU-h; API ~$200–300 more (code cap $1,500; Flash draws on the OpenRouter key's $1k/week limit).
- **Budget so far:** $293 API of $2k for the pilot, plus ~6 GPU-h used (about 3 lost to failed jobs).
- **Stop it:** `kubectl -n research delete job pfau-explain-pilot-1007-215037`
- **Cleanup:** the Job and its code ConfigMap are deleted 24 h after finishing; the shared PVC and results are kept.
- **Outcome:** succeeded at 22:19 UTC (29 min). Redid the 254 cut-off Qwen consolidations (none cut off again), no API failures; total pilot API spend $342.78. Its health section then showed Queen's evaluation signs misread in 62% of analyses, fixed in f067dec.

## pfau-explain-inspect (2026-10-07, twice: 21:52 and 23:05 UTC)

- CPU-only pod (2 CPU, 8Gi, cpu queue, python:3.12-slim) mounting `pfau-explain-fs` to read run logs and caches and copy the report off the volume; at most 1 h each, deleted when done; no GPU, no API spend.

## pfau-explain-pilot-1007-205100

- **Job:** gpu queue, from JacobPfau/queen@bf08815, submitted 2026-10-07 20:51 UTC.
- **What it does:** same debugging run as the job below, with the Stockfish setup check fixed and failures written straight to the pod log.
- **Requests:** 4× H200, 64 CPU, 900Gi memory; storage `pfau-explain-fs` (1Ti crusoe-fs); models and venv on the pod's own disk.
- **Expected runtime:** 1.5–2.5 h including ~10 min of setup, done around 22:30–23:30 UTC; hard limit 48 h.
- **Expected cost:** ~6–10 GPU-h; API ~$500 (code cap $1,500; Flash draws on the OpenRouter key's $1k/week limit).
- **Budget so far:** ~$0.05 of $2k for the pilot, plus ~3 GPU-h lost to the two failed jobs below.
- **Stop it:** `kubectl -n research delete job pfau-explain-pilot-1007-205100`
- **Cleanup:** the Job and its code ConfigMap are deleted 24 h after finishing; the shared PVC and results are kept.
- **Outcome:** ran rounds 1–3 (21:02–21:48 UTC), then crashed at the start of round 4 on a full Qwen consolidation with no parseable heads. The run also showed 26% of Qwen outputs cut off at 8192 tokens and 119 Flash calls rate-limited (OpenRouter's 300 requests/min). Fixed in edfd3ef. Spent $293 API and ~3 GPU-h; all results are cached.

## pfau-explain-pilot-1007-203643

- **Job:** gpu queue, from JacobPfau/queen@5ca73a9, submitted 2026-10-07 20:36 UTC.
- **What it does:** runs the pilot end to end on 100 positions as a debugging run (health counts, persistent run logs in `/data/runs/<job>`), with Queen and Qwen requests split across 4 GPUs.
- **Requests:** 4× H200, 64 CPU, 900Gi memory; storage `pfau-explain-fs` (1Ti crusoe-fs, new); models and venv on the pod's own disk.
- **Expected runtime:** 1.5–2.5 h including ~15 min of downloads, done around 22:00–23:00 UTC; hard limit 48 h.
- **Expected cost:** ~6–10 GPU-h; API ~$500 (code cap $1,500; Flash draws on the OpenRouter key's $1k/week limit).
- **Budget so far:** ~$0.05 of $2k for the pilot, plus ~2.5 GPU-h lost to the stuck job below.
- **Stop it:** `kubectl -n research delete job pfau-explain-pilot-1007-203643`
- **Cleanup:** the Job and its code ConfigMap are deleted 24 h after finishing; the shared PVC and results are kept.
- **Outcome:** failed at the end of setup (20:49 UTC): checking Stockfish's version through `grep -m1` triggered SIGPIPE, which `pipefail` made fatal (fixed in bf08815). The automatic retry pod was deleted at 20:50. No API spend; ~0.9 GPU-h.

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
