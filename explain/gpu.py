"""GPU worker: run pending Queen or Qwen requests and store the results.

The pilot's CPU/API stages write request files; this worker answers every
request whose key is not yet in the output store, so it is resumable and can
run on a different machine from the rest of the pipeline.

    python -m explain.gpu queen --requests R.jsonl --store S.jsonl \
        --model /data/models/queen_hce-4 --prompt "..."
    python -m explain.gpu qwen --requests R.jsonl --store S.jsonl \
        --model models/Qwen3.8-27B

Queen runs through the released Flamingo checkpoints (princeton-nlp/queen_*),
with the release's inference settings except a longer context, which reading
a pre-filled analysis needs.

Queen request: {key, fen, history, prefix?, seed, max_tokens}
Qwen request:  {key, system, user, max_tokens?}
"""

from __future__ import annotations

import argparse
import hashlib
import os
import time
from pathlib import Path

os.environ.setdefault("VLLM_USE_FLASHINFER_SAMPLER", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

from datagen.self_distill.consolidation import strip_thinking
from explain.common import Store, read_jsonl


def pending(requests_path: Path, store: Store, shard: int = 0, num_shards: int = 1) -> list[dict]:
    """Unanswered requests in this worker's shard (requests split by key hash)."""
    rows = read_jsonl(requests_path)
    seen, todo = set(), []
    for row in rows:
        if row["key"] in store or row["key"] in seen:
            continue
        if int(hashlib.md5(row["key"].encode()).hexdigest(), 16) % num_shards != shard:
            continue
        seen.add(row["key"])
        todo.append(row)
    return todo


def queen_generator(args):
    """The release's Flamingo generator, able to pre-fill each response."""
    from models.vllm.flamingo_generate import ChessFlamingoGenerator

    class PrefixGenerator(ChessFlamingoGenerator):
        prefixes = None

        def _prompt_ids(self, prompt):
            ids = super()._prompt_ids(prompt)
            prefix = next(self.prefixes, "") if self.prefixes is not None else ""
            return ids + (self.tok.encode(prefix, add_special_tokens=False) if prefix else [])

    return PrefixGenerator(
        args.model, args.model / "lc0", dtype="bfloat16",
        gpu_memory_utilization=args.gpu_memory_utilization,
        max_model_len=args.max_model_len, max_num_seqs=64, seed=20260823,
        enforce_eager=True, use_v1_vllm=True,
    )


def run_queen(args) -> None:
    store = Store(args.store)
    todo = pending(args.requests, store, args.shard, args.num_shards)
    print(f"[queen] {len(todo)} pending requests", flush=True)
    if not todo:
        return
    generator = queen_generator(args)
    # Batch requests with the same token budget together, so short reads are
    # never given a full generation's 2048-token budget.
    todo.sort(key=lambda row: row.get("max_tokens", 2048))
    chunks = [todo[i:i + args.chunk] for i in range(0, len(todo), args.chunk)]
    chunks = [[r for r in c if r.get("max_tokens", 2048) == m]
              for c in chunks for m in sorted({r.get("max_tokens", 2048) for r in c})]
    done = 0
    for chunk in chunks:
        done += len(chunk)
        began = time.perf_counter()
        # _prompt_ids runs once per request, in order, inside generate().
        generator.prefixes = iter([row.get("prefix") or "" for row in chunk])
        outputs = generator.generate(
            [row["fen"] for row in chunk],
            [args.prompt] * len(chunk),
            [row.get("history") or [] for row in chunk],
            temperature=args.temperature, top_k=20, top_p=0.95, repetition_penalty=1.0,
            max_tokens=max(row.get("max_tokens", 2048) for row in chunk),
            seeds=[row["seed"] for row in chunk],
        )
        generator.prefixes = None
        seconds = time.perf_counter() - began
        for row, output in zip(chunk, outputs):
            store.put(row["key"], {
                "text": output["text"],
                "output_tokens": len(output["token_ids"]),
                "finish_reason": output.get("finish_reason"),
                "prefix": row.get("prefix") or "",
                "batch_seconds": seconds,
                "batch_size": len(chunk),
            })
        print(f"[queen] {done}/{len(todo)} in {seconds:.0f}s", flush=True)


def run_qwen(args) -> None:
    from vllm import LLM, SamplingParams
    store = Store(args.store)
    todo = pending(args.requests, store, args.shard, args.num_shards)
    print(f"[qwen] {len(todo)} pending requests", flush=True)
    if not todo:
        return
    # Same inference settings as the self-distill consolidation recipe.
    llm = LLM(
        model=str(args.model), tensor_parallel_size=args.tensor_parallel,
        max_model_len=args.max_model_len, max_num_seqs=64,
        gpu_memory_utilization=args.gpu_memory_utilization, trust_remote_code=True,
        language_model_only=True, enable_prefix_caching=False,
        gdn_prefill_backend="triton",
    )
    tokenizer = llm.get_tokenizer()
    params = SamplingParams(temperature=1.0, top_p=0.95, top_k=20,
                            max_tokens=args.max_output_tokens)
    for start in range(0, len(todo), args.chunk):
        chunk = todo[start:start + args.chunk]
        prompts = [
            tokenizer.apply_chat_template(
                [{"role": "system", "content": row["system"]},
                 {"role": "user", "content": row["user"]}],
                tokenize=False, add_generation_prompt=True, reasoning_effort="low",
            )
            for row in chunk
        ]
        began = time.perf_counter()
        outputs = llm.generate(prompts, params, use_tqdm=False)
        seconds = time.perf_counter() - began
        for row, output in zip(chunk, outputs):
            completion = output.outputs[0]
            store.put(row["key"], {
                "text": strip_thinking(completion.text),
                "output_tokens": len(completion.token_ids),
                "input_tokens": len(output.prompt_token_ids),
                "finish_reason": completion.finish_reason,
                "batch_seconds": seconds,
                "batch_size": len(chunk),
            })
        print(f"[qwen] {start + len(chunk)}/{len(todo)} in {seconds:.0f}s", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("worker", choices=["queen", "qwen"])
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--prompt", help="Queen's analysis prompt (the model's own)")
    parser.add_argument("--chunk", type=int, default=256)
    parser.add_argument("--temperature", type=float, default=0.6)
    parser.add_argument("--max-model-len", type=int, default=None)
    parser.add_argument("--max-output-tokens", type=int, default=8192)
    parser.add_argument("--gpu-memory-utilization", type=float, default=None)
    parser.add_argument("--tensor-parallel", type=int, default=1)
    parser.add_argument("--shard", type=int, default=0, help="this worker's shard (one per GPU)")
    parser.add_argument("--num-shards", type=int, default=1)
    args = parser.parse_args()
    if args.worker == "queen":
        args.max_model_len = args.max_model_len or 4096
        args.gpu_memory_utilization = args.gpu_memory_utilization or 0.72
        if not args.prompt:
            parser.error("--prompt is required for queen")
        run_queen(args)
    else:
        args.max_model_len = args.max_model_len or 16384
        args.gpu_memory_utilization = args.gpu_memory_utilization or 0.92
        run_qwen(args)


if __name__ == "__main__":
    main()
