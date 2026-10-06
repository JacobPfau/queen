#!/usr/bin/env bash
# Idempotent setup on the pilot PVC (/data): uv, the Queen release environment,
# model weights, and Stockfish. Each step leaves a marker and is skipped next time.
set -euo pipefail
DATA=/data
mkdir -p "$DATA/bin" "$DATA/models" "$DATA/markers" "$DATA/cache"
export UV_CACHE_DIR="$DATA/cache/uv" HF_HOME="$DATA/cache/hf" PATH="$DATA/bin:$PATH"

done_() { touch "$DATA/markers/$1"; }
is_done() { [ -f "$DATA/markers/$1" ]; }

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
  curl -LsSf -o "$tmp/sf.tar" \
    https://github.com/official-stockfish/Stockfish/releases/latest/download/stockfish-ubuntu-x86-64-avx2.tar
  tar -xf "$tmp/sf.tar" -C "$tmp"
  install -m 755 "$(find "$tmp" -type f -name 'stockfish-ubuntu-x86-64-avx2' | head -1)" "$DATA/bin/stockfish"
  rm -rf "$tmp"
  done_ stockfish
fi
echo "[setup] done"
