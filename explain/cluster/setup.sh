#!/usr/bin/env bash
# Setup for one pod. Two tiers, as the cluster README recommends:
#   /data   shared crusoe-fs volume (persists): results, uv and HF caches,
#           the uv and Stockfish binaries. Markers in /data/markers.
#   /local  the container's own filesystem on the node's NVMe (rebuilt every
#           pod): the venv, uv's interpreters and the model weights, which
#           several GPU workers read at once, faster locally than over NFS.
# SKIP_MODELS=1 skips the weight downloads (report-only jobs).
set -euo pipefail
DATA=/data
LOCAL=/local
mkdir -p "$DATA/bin" "$DATA/markers" "$DATA/cache" "$LOCAL/models" "$LOCAL/markers"
export UV_CACHE_DIR="$DATA/cache/uv" UV_PYTHON_INSTALL_DIR="$LOCAL/uv-python" \
       HF_HOME="$DATA/cache/hf" PATH="$DATA/bin:$PATH" UV_LINK_MODE=copy

done_() { touch "$1/markers/$2"; }
is_done() { [ -f "$1/markers/$2" ]; }
step() { echo "[setup] $(date -u +%H:%M:%S) $*"; }

# Container packages do not persist. Triton compiles a small CUDA helper at
# runtime and needs a C compiler.
if ! command -v curl >/dev/null || ! command -v gcc >/dev/null; then
  step "apt packages"
  apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    curl ca-certificates tar gcc libc6-dev >/dev/null
fi

if ! is_done "$DATA" uv; then
  step "uv"
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$DATA/bin" UV_NO_MODIFY_PATH=1 sh
  done_ "$DATA" uv
fi

if ! is_done "$LOCAL" venv; then
  step "venv"
  uv venv --python 3.12.12 "$LOCAL/venv"
  uv pip install --python "$LOCAL/venv/bin/python" huggingface-hub==1.27.0
  # The release's pinned inference environment (its requirements file alone,
  # without the weights), plus the pilot's own needs.
  "$LOCAL/venv/bin/hf" download princeton-nlp/queen_pawn-8 requirements-inference.txt \
    --local-dir "$LOCAL/models/queen_pawn-8"
  uv pip sync --python "$LOCAL/venv/bin/python" "$LOCAL/models/queen_pawn-8/requirements-inference.txt"
  uv pip install --python "$LOCAL/venv/bin/python" anthropic google-genai httpx PyYAML
  done_ "$LOCAL" venv
fi

if [ "${SKIP_MODELS:-0}" != 1 ]; then
  for repo in princeton-nlp/queen_pawn-8 Qwen/Qwen3.8-27B; do
    name=${repo#*/}
    if ! is_done "$LOCAL" "model-$name"; then
      step "download $repo"
      "$LOCAL/venv/bin/hf" download "$repo" --local-dir "$LOCAL/models/$name"
      done_ "$LOCAL" "model-$name"
    fi
  done
fi

if ! is_done "$DATA" stockfish; then
  step "stockfish"
  tmp=$(mktemp -d)
  # Pinned release, so oracle scores do not change with new Stockfish versions.
  curl -LsSf -o "$tmp/sf.tar.gz" \
    https://github.com/official-stockfish/Stockfish/releases/download/sf_19/stockfish-linux-x86-64-universal.tar.gz
  tar -xzf "$tmp/sf.tar.gz" -C "$tmp"
  install -m 755 "$(find "$tmp" -type f -name 'stockfish-linux-x86-64-universal*' ! -name '*.tar.gz' | head -1)" \
    "$DATA/bin/stockfish"
  rm -rf "$tmp"
  done_ "$DATA" stockfish
fi
echo "uci" | "$DATA/bin/stockfish" | grep -m1 "^id name"
step "done"
