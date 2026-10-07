#!/usr/bin/env bash
# Idempotent setup on the pilot PVC (/data): uv, the Queen release environment,
# model weights, and Stockfish. Each step leaves a marker and is skipped next time.
set -euo pipefail
DATA=/data
mkdir -p "$DATA/bin" "$DATA/models" "$DATA/markers" "$DATA/cache"
# uv's interpreters live on the PVC too: the venv links to them, and the
# container's own home directory does not survive the pod.
export UV_CACHE_DIR="$DATA/cache/uv" UV_PYTHON_INSTALL_DIR="$DATA/uv-python" \
       HF_HOME="$DATA/cache/hf" PATH="$DATA/bin:$PATH"

done_() { touch "$DATA/markers/$1"; }
is_done() { [ -f "$DATA/markers/$1" ]; }

# A venv whose interpreter is gone must be rebuilt, with its packages.
if is_done venv && ! "$DATA/venv/bin/python" -V >/dev/null 2>&1; then
  rm -rf "$DATA/venv" "$DATA/markers/venv" "$DATA/markers/deps"
fi

if ! command -v curl >/dev/null; then
  apt-get update -qq && apt-get install -y -qq --no-install-recommends curl ca-certificates tar >/dev/null
fi

if ! is_done uv; then
  curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="$DATA/bin" UV_NO_MODIFY_PATH=1 sh
  done_ uv
fi

if ! is_done venv; then
  uv venv --python 3.12.12 "$DATA/venv"
  uv pip install --python "$DATA/venv/bin/python" huggingface-hub==1.27.0
  done_ venv
fi

for repo in princeton-nlp/queen_hce-4 princeton-nlp/queen_pawn-8; do
  name=${repo#*/}
  if ! is_done "model-$name"; then
    "$DATA/venv/bin/hf" download "$repo" --local-dir "$DATA/models/$name"
    done_ "model-$name"
  fi
done

if ! is_done deps; then
  # The release's pinned inference environment, plus the pilot's own needs.
  uv pip sync --python "$DATA/venv/bin/python" "$DATA/models/queen_pawn-8/requirements-inference.txt"
  uv pip install --python "$DATA/venv/bin/python" anthropic google-genai PyYAML
  done_ deps
fi

if ! is_done model-qwen; then
  "$DATA/venv/bin/hf" download Qwen/Qwen3.8-27B --local-dir "$DATA/models/Qwen3.8-27B"
  done_ model-qwen
fi

if ! is_done stockfish; then
  tmp=$(mktemp -d)
  # Pinned release, so oracle scores do not change with new Stockfish versions.
  curl -LsSf -o "$tmp/sf.tar.gz" \
    https://github.com/official-stockfish/Stockfish/releases/download/sf_19/stockfish-linux-x86-64-universal.tar.gz
  tar -xzf "$tmp/sf.tar.gz" -C "$tmp"
  install -m 755 "$(find "$tmp" -type f -name 'stockfish-linux-x86-64-universal*' ! -name '*.tar.gz' | head -1)" \
    "$DATA/bin/stockfish"
  echo "uci" | "$DATA/bin/stockfish" | grep -m1 "^id name"
  rm -rf "$tmp"
  done_ stockfish
fi
echo "[setup] done"
