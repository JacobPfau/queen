# Explanation-utility pilot

Purpose and design: `claude/AGENTS.md`, `claude/experiment_choices.md`.
Budget: $2k for the pilot; the API cap in `configs/explain/pilot.yaml` is $1.5k.

## Needs

- GPU node with the repo's `.venv` (vLLM installed), plus:
  `data/engines/stockfish_*`, `data/engines/lc0_hf_bt5`, Queen's merged
  checkpoint (`runs/self_distill/iteration/merged`) and `models/Qwen3.8-27B`.
- `ANTHROPIC_API_KEY` and `GEMINI_API_KEY` in the environment.
- The Flash model id and prices filled in under `models.flash` in the config.

## Loop

```bash
python -m explain.pilot --config configs/explain/pilot.yaml advance        # projection only
python -m explain.pilot --config configs/explain/pilot.yaml advance --yes  # spend, up to the cap
# then run the GPU commands it prints (explain/gpu.py queen|qwen ...), and repeat
python -m explain.pilot --config configs/explain/pilot.yaml report
```

Each `advance` does every step whose inputs exist; every result is cached, so
reruns never repeat GPU work or API spend. Expect about four rounds: Queen
root analyses, Queen child analyses, hybrid writing and consolidation, then
Queen and external reading.

## Queen as reader

Queen reads a text by pre-filling `ANALYSIS:\n<prose>\nBEST_MOVE:` and writing
the remaining head fields. The smoke test showed that pre-filling only the
ANALYSIS field lets Queen continue with an analysis of its own.

## Outputs (in `runs/explain/pilot/`)

- `report.md`: model-substitution table (Flash and Sonnet against Opus, per
  role), writer vocabulary compliance, API and GPU cost, all cells.
- `samples.md`: texts and stated reasons for 10 positions, for reading.
- `decisions.jsonl`: one row per position and cell.
