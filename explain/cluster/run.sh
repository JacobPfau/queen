#!/usr/bin/env bash
# Pod entrypoint: unpack the code, set up the PVC, then run the pilot to completion.
#   MODE=smoke  check CUDA, Queen generation on two positions, and the Qwen load
#   MODE=pilot  loop `advance` and the GPU workers until nothing is pending, then report
set -euo pipefail
export PATH=/data/bin:$PATH HF_HOME=/data/cache/hf TOKENIZERS_PARALLELISM=false
export VLLM_ENABLE_V1_MULTIPROCESSING=0 VLLM_USE_FLASHINFER_SAMPLER=0 \
       VLLM_DISABLE_REQUEST_ID_RANDOMIZATION=1 OMP_NUM_THREADS=1
rm -rf /data/code && mkdir -p /data/code && tar -xzf /code/code.tgz -C /data/code
bash /data/code/explain/cluster/setup.sh
cd /data/code
export PYTHONPATH=/data/code
PY=/data/venv/bin/python
CFG=configs/explain/pilot.yaml
WORK=$($PY -c "import yaml; print(yaml.safe_load(open('$CFG'))['workdir'])")
QUEEN=$($PY -c "import yaml; print(yaml.safe_load(open('$CFG'))['queen_model'])")
PROMPT=$($PY -c "import yaml; print(yaml.safe_load(open('$CFG'))['queen_prompt'])")
QWEN=$($PY -c "import yaml; print(yaml.safe_load(open('$CFG'))['qwen_model'])")
mkdir -p "$WORK"

if [ "${MODE:-pilot}" = smoke ]; then
  nvidia-smi --query-gpu=name,driver_version --format=csv
  $PY -c "import torch; print('torch', torch.__version__, 'cuda', torch.version.cuda, 'available', torch.cuda.is_available())"
  S=/data/work/smoke && mkdir -p $S
  $PY - <<'EOF'
import json
from explain.common import write_jsonl
fens = ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3"]
rows = [{"key": f"gen{i}", "fen": f, "history": [], "seed": i, "max_tokens": 2048} for i, f in enumerate(fens)]
rows.append({"key": "read0", "fen": fens[1], "history": [], "seed": 7, "max_tokens": 400,
             "prefix": "ANALYSIS:\nBlack should develop the knight to f6 and attack e4.\n"})
write_jsonl("/data/work/smoke/queen_requests.jsonl", rows)
write_jsonl("/data/work/smoke/qwen_requests.jsonl",
            [{"key": "q0", "system": "Answer briefly.", "user": "Name one chess opening."}])
EOF
  rm -f $S/queen_store.jsonl $S/qwen_store.jsonl
  $PY -m explain.gpu queen --requests $S/queen_requests.jsonl --store $S/queen_store.jsonl \
      --model "$QUEEN" --prompt "$PROMPT"
  $PY -m explain.gpu qwen --requests $S/qwen_requests.jsonl --store $S/qwen_store.jsonl --model "$QWEN"
  $PY -c "
import json
for line in open('$S/queen_store.jsonl'):
    r = json.loads(line); print('=====', r['key'], r['output_tokens'], r.get('finish_reason')); print(r['prefix'] + r['text'][:1500])
for line in open('$S/qwen_store.jsonl'):
    r = json.loads(line); print('===== qwen', r['output_tokens'], r['finish_reason']); print(r['text'][:500])
"
  echo "[smoke] done"
  exit 0
fi

for round in $(seq 1 15); do
  echo "=== round $round $(date -u +%H:%M:%S)"
  $PY -m explain.pilot --config $CFG advance --yes
  status=$(cat "$WORK/status.json")
  queen=$($PY -c "import json; print(json.load(open('$WORK/status.json'))['queen_pending'])")
  qwen=$($PY -c "import json; print(json.load(open('$WORK/status.json'))['qwen_pending'])")
  if [ "$queen" -gt 0 ]; then
    $PY -m explain.gpu queen --requests "$WORK/queen_requests.jsonl" --store "$WORK/queen_store.jsonl" \
        --model "$QUEEN" --prompt "$PROMPT"
  fi
  if [ "$qwen" -gt 0 ]; then
    $PY -m explain.gpu qwen --requests "$WORK/qwen_requests.jsonl" --store "$WORK/qwen_store.jsonl" \
        --model "$QWEN"
  fi
  if [ "$queen" -eq 0 ] && [ "$qwen" -eq 0 ]; then
    $PY -m explain.pilot --config $CFG advance --yes
    api=$($PY -c "import json; print(json.load(open('$WORK/status.json'))['api_pending'])")
    [ "$api" -eq 0 ] && break
    echo "[run] $api API requests still pending (failures or budget); retrying next round"
  fi
done
$PY -m explain.pilot --config $CFG report
echo "[run] finished $(date -u +%H:%M:%S); $(cat "$WORK/status.json")"
