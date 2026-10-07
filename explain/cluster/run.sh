#!/usr/bin/env bash
# Pod entrypoint: unpack the code, set up, then run the requested mode.
#   MODE=smoke  check CUDA, Queen generation on two positions, and the Qwen load
#   MODE=pilot  loop `advance` and the GPU workers until nothing is pending, then report
#   MODE=report re-score cached results and rewrite the report (CPU only)
# Everything this pod prints is also kept in /data/runs/<job>/run.log, with
# meta.json (commit, pod, node, GPUs) and per-round GPU worker logs, so a run
# can be debugged after its pod is gone.
set -euo pipefail
JOB=${JOB_NAME:-unknown-job}
RUNDIR=/data/runs/$JOB
mkdir -p "$RUNDIR"
exec 3>&2  # the pod's own stderr, which survives even if tee is killed first
exec > >(tee -a "$RUNDIR/run.log") 2>&1
STAGE=start
fail() {
  local msg="[run] FAILED in stage \"$STAGE\" (line $1, exit $2) at $(date -u +%H:%M:%S)"
  echo "$msg" >&3; echo "$msg" >> "$RUNDIR/run.log"
}
trap 'fail $LINENO $?' ERR
stage() { STAGE=$1; echo "[run] $(date -u +%H:%M:%S) stage: $1"; }
echo "[run] job=$JOB pod=${POD_NAME:-?} node=${NODE_NAME:-?} commit=${JOB_COMMIT:-?} mode=${MODE:-pilot}"

export PATH=/data/bin:$PATH HF_HOME=/data/cache/hf UV_PYTHON_INSTALL_DIR=/local/uv-python \
       TOKENIZERS_PARALLELISM=false
export VLLM_ENABLE_V1_MULTIPROCESSING=0 VLLM_USE_FLASHINFER_SAMPLER=0 \
       VLLM_DISABLE_REQUEST_ID_RANDOMIZATION=1 OMP_NUM_THREADS=1
stage setup
mkdir -p /local/code && tar -xzf /code/code.tgz -C /local/code
[ "${MODE:-pilot}" = report ] && export SKIP_MODELS=1
bash /local/code/explain/cluster/setup.sh
cd /local/code
export PYTHONPATH=/local/code
PY=/local/venv/bin/python
CFG=configs/explain/pilot.yaml
WORK=$($PY -c "import yaml; print(yaml.safe_load(open('$CFG'))['workdir'])")
QUEEN=$($PY -c "import yaml; print(yaml.safe_load(open('$CFG'))['queen_model'])")
PROMPT=$($PY -c "import yaml; print(yaml.safe_load(open('$CFG'))['queen_prompt'])")
QWEN=$($PY -c "import yaml; print(yaml.safe_load(open('$CFG'))['qwen_model'])")
mkdir -p "$WORK"
NGPU=$(nvidia-smi -L 2>/dev/null | wc -l || echo 0)
GPUINFO=$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | sort | uniq -c | tr -s ' ' || echo none)
$PY - <<PYEOF
import json, os, socket, time
json.dump({"job": "$JOB", "pod": os.environ.get("POD_NAME"), "node": os.environ.get("NODE_NAME"),
           "commit": os.environ.get("JOB_COMMIT"), "mode": os.environ.get("MODE", "pilot"),
           "gpus": $NGPU, "gpu_info": """$GPUINFO""".strip(), "workdir": "$WORK",
           "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())},
          open("$RUNDIR/meta.json", "w"), indent=1)
PYEOF
echo "[run] $NGPU GPUs: $GPUINFO"

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
             "prefix": "ANALYSIS:\nBlack should develop the knight to f6 and attack e4.\nBEST_MOVE:"})
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

if [ "${MODE:-pilot}" = report ]; then  # re-score cached results; no GPU or API work
  stage report
  $PY -m explain.pilot --config $CFG report
  exit 0
fi

# One worker per GPU, each on its own shard of the requests and its own store
# file; shard files are merged into the main store afterwards (and at the start
# of each round, in case a previous pod died mid-batch).
merge() {  # merge <worker>
  for f in "$WORK/$1_store.shard"*.jsonl; do
    [ -e "$f" ] || continue
    cat "$f" >> "$WORK/$1_store.jsonl" && rm "$f"
  done
}
gpu_workers() {  # gpu_workers <worker> <round> <model> [extra args...]
  local worker=$1 round=$2 model=$3; shift 3
  local pids=() started=$SECONDS
  for i in $(seq 0 $((NGPU - 1))); do
    CUDA_VISIBLE_DEVICES=$i $PY -m explain.gpu "$worker" --requests "$WORK/${worker}_requests.jsonl" \
      --store "$WORK/${worker}_store.shard$i.jsonl" --model "$model" \
      --shard "$i" --num-shards "$NGPU" "$@" > "$RUNDIR/${worker}_r${round}_gpu$i.log" 2>&1 &
    pids+=($!)
  done
  local failed=0
  for pid in "${pids[@]}"; do wait "$pid" || failed=1; done
  for i in $(seq 0 $((NGPU - 1))); do
    echo "--- ${worker} gpu$i (round $round)"; grep -E "^\[$worker\]|Error|Traceback" "$RUNDIR/${worker}_r${round}_gpu$i.log" | tail -n 4 || true
  done
  echo "[run] $worker round $round took $((SECONDS - started))s on $NGPU GPUs (failed=$failed)"
  merge "$worker"
  return $failed
}

for round in $(seq 1 15); do
  echo "=== round $round $(date -u +%H:%M:%S)"
  merge queen; merge qwen
  stage "advance r$round"
  $PY -m explain.pilot --config $CFG advance --yes
  queen=$($PY -c "import json; print(json.load(open('$WORK/status.json'))['queen_pending'])")
  qwen=$($PY -c "import json; print(json.load(open('$WORK/status.json'))['qwen_pending'])")
  if [ "$queen" -gt 0 ]; then stage "queen r$round"; gpu_workers queen "$round" "$QUEEN" --prompt "$PROMPT"; fi
  if [ "$qwen" -gt 0 ]; then stage "qwen r$round"; gpu_workers qwen "$round" "$QWEN"; fi
  if [ "$queen" -eq 0 ] && [ "$qwen" -eq 0 ]; then
    stage "final advance r$round"
    $PY -m explain.pilot --config $CFG advance --yes
    api=$($PY -c "import json; print(json.load(open('$WORK/status.json'))['api_pending'])")
    [ "$api" -eq 0 ] && break
    echo "[run] $api API requests still pending (failures or budget); retrying next round"
  fi
done
stage report
$PY -m explain.pilot --config $CFG report
cp "$WORK/report.md" "$WORK/samples.md" "$WORK/status.json" "$RUNDIR/" 2>/dev/null || true
echo "[run] finished $(date -u +%H:%M:%S); $(cat "$WORK/status.json")"
