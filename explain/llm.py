"""External LLM calls (OpenRouter, Anthropic, Gemini) with caching and a hard spend cap.

Every call is cached in a Store keyed by (model, effort, system, user), so a
rerun costs nothing. Spend is the sum of recorded call costs; once it reaches
``max_spend_usd`` new calls raise ``BudgetExceeded``. No refusal fallback is
configured: a fallback would silently answer with a different model and
contaminate the arm, so refusals are recorded as failures instead.
"""

from __future__ import annotations

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from explain.common import Store, stable_hash


class BudgetExceeded(RuntimeError):
    pass


@dataclass
class ModelSpec:
    name: str              # arm label, e.g. "opus"
    provider: str          # "openrouter" | "anthropic" | "gemini"
    model: str             # API model id
    price_in: float | None # USD per million input tokens
    price_out: float | None  # USD per million output tokens (thinking included)
    effort: str = "medium"
    thinking_levels: dict = field(default_factory=dict)  # gemini: effort -> thinking_level

    def cost(self, tokens_in: int, tokens_out: int) -> float:
        if self.price_in is None or self.price_out is None:
            raise ValueError(f"set price_in and price_out for model '{self.name}' in the config")
        return (tokens_in * self.price_in + tokens_out * self.price_out) / 1e6


class Ledger:
    """Spend across all models, rebuilt from the call cache on start-up."""

    def __init__(self, store: Store, max_spend_usd: float):
        self.store = store
        self.max_spend = max_spend_usd
        self.lock = threading.Lock()
        self.spent = sum(row.get("cost_usd", 0.0) for row in store.values())

    def check(self) -> None:
        if self.spent >= self.max_spend:
            raise BudgetExceeded(
                f"API spend ${self.spent:.2f} reached the cap ${self.max_spend:.2f}"
            )

    def add(self, cost: float) -> None:
        with self.lock:
            self.spent += cost


class Caller:
    def __init__(self, specs: dict[str, ModelSpec], cache_path: Path,
                 max_spend_usd: float, concurrency: dict[str, int] | None = None):
        """``concurrency`` caps in-flight calls per model (default 16 each)."""
        self.specs = specs
        self.store = Store(cache_path)
        self.ledger = Ledger(self.store, max_spend_usd)
        self.concurrency = {name: (concurrency or {}).get(name, 16) for name in specs}
        self._slots = {name: threading.Semaphore(n) for name, n in self.concurrency.items()}
        self._clients: dict[str, object] = {}
        self._client_lock = threading.Lock()

    # ------------------------------------------------------------- clients

    def _client(self, provider: str):
        with self._client_lock:
            if provider not in self._clients:
                if provider == "anthropic":
                    import anthropic
                    self._clients[provider] = anthropic.Anthropic(max_retries=6)
                elif provider == "gemini":
                    from google import genai
                    self._clients[provider] = genai.Client(
                        api_key=os.environ.get("GEMINI_API_KEY")
                        or os.environ.get("GOOGLE_API_KEY")
                    )
                else:
                    raise ValueError(f"unknown provider {provider}")
            return self._clients[provider]

    def _anthropic(self, spec: ModelSpec, effort: str, system: str, user: str,
                   max_tokens: int) -> dict:
        client = self._client("anthropic")
        # Streaming avoids HTTP timeouts on long thinking; the final message is
        # what we need. Thinking is adaptive by default on Opus/Sonnet 5.5.
        with client.messages.stream(
            model=spec.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            output_config={"effort": effort},
        ) as stream:
            message = stream.get_final_message()
        text = "".join(block.text for block in message.content if block.type == "text")
        return {
            "text": text,
            "stop_reason": message.stop_reason,
            "tokens_in": message.usage.input_tokens,
            "tokens_out": message.usage.output_tokens,
            "request_id": getattr(message, "_request_id", None),
        }

    def _openrouter(self, spec: ModelSpec, effort: str, system: str, user: str,
                    max_tokens: int) -> dict:
        """One OpenAI-style chat completion through OpenRouter.

        ``reasoning.effort`` maps to Claude's effort and Gemini's thinking level;
        reasoning tokens are billed as output. OpenRouter reports the charged
        cost in ``usage.cost``, which is recorded when present.
        """
        import httpx
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}"},
            json={
                "model": spec.model,
                "messages": [{"role": "system", "content": system},
                             {"role": "user", "content": user}],
                "max_tokens": max_tokens,
                "reasoning": {"effort": effort},
                "usage": {"include": True},
            },
            timeout=900,
        )
        if response.status_code != 200:
            error = RuntimeError(f"OpenRouter {response.status_code}: {response.text[:300]}")
            error.status_code = response.status_code
            raise error
        data = response.json()
        if "error" in data:
            error = RuntimeError(f"OpenRouter error: {str(data['error'])[:300]}")
            error.status_code = data["error"].get("code") if isinstance(data["error"], dict) else None
            raise error
        choice = data["choices"][0]
        usage = data.get("usage") or {}
        return {
            "text": choice["message"].get("content") or "",
            "stop_reason": "refusal" if choice.get("finish_reason") in ("refusal", "content_filter")
                           else choice.get("finish_reason"),
            "tokens_in": usage.get("prompt_tokens", 0),
            "tokens_out": usage.get("completion_tokens", 0),
            "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
            "billed_usd": usage.get("cost"),
            "provider": data.get("provider"),
            "request_id": data.get("id"),
        }

    def _gemini(self, spec: ModelSpec, effort: str, system: str, user: str,
                max_tokens: int) -> dict:
        from google.genai import types
        client = self._client("gemini")
        config = {"system_instruction": system, "max_output_tokens": max_tokens}
        level = spec.thinking_levels.get(effort)
        if level:
            config["thinking_config"] = types.ThinkingConfig(thinking_level=level)
        response = client.models.generate_content(
            model=spec.model,
            contents=user,
            config=types.GenerateContentConfig(**config),
        )
        usage = response.usage_metadata
        tokens_out = (usage.candidates_token_count or 0) + (usage.thoughts_token_count or 0)
        finish = response.candidates[0].finish_reason if response.candidates else None
        return {
            "text": response.text or "",
            "stop_reason": str(finish),
            "tokens_in": usage.prompt_token_count or 0,
            "tokens_out": tokens_out,
            "request_id": getattr(response, "response_id", None),
        }

    # ---------------------------------------------------------------- calls

    def key(self, model: str, system: str, user: str, effort: str | None = None,
            tag: str = "") -> str:
        spec = self.specs[model]
        return stable_hash([spec.model, effort or spec.effort, system, user, tag])

    def call(self, model: str, system: str, user: str, *, effort: str | None = None,
             max_tokens: int = 16000, tag: str = "") -> dict:
        spec = self.specs[model]
        effort = effort or spec.effort
        key = self.key(model, system, user, effort, tag)
        cached = self.store.get(key)
        if cached is not None and not cached.get("error"):
            return cached  # recorded failures are retried on the next run
        self.ledger.check()
        call = {"openrouter": self._openrouter, "anthropic": self._anthropic,
                "gemini": self._gemini}[spec.provider]
        started = time.time()
        last_error = None
        for attempt in range(3):
            try:
                result = call(spec, effort, system, user, max_tokens)
                break
            except BudgetExceeded:
                raise
            except Exception as error:  # SDK retries transport errors already
                last_error = error
                status = getattr(error, "status_code", None) or getattr(error, "code", None)
                if isinstance(status, int) and 400 <= status < 500 and status != 429:
                    break  # bad key, bad request: retrying cannot help
                time.sleep(5 * (attempt + 1))
        else:
            # Persist the failure (zero cost) so analysis can count it.
            return self.store.put(key, {
                "model": model, "effort": effort, "tag": tag, "text": "",
                "error": repr(last_error), "cost_usd": 0.0,
                "tokens_in": 0, "tokens_out": 0, "seconds": time.time() - started,
            })
        cost = (result["billed_usd"] if result.get("billed_usd") is not None
                else spec.cost(result["tokens_in"], result["tokens_out"]))
        self.ledger.add(cost)
        return self.store.put(key, {
            "model": model, "effort": effort, "tag": tag, **result,
            "error": None, "cost_usd": cost, "seconds": time.time() - started,
        })

    def map(self, requests: list[dict]) -> list[dict]:
        """Run many ``call`` kwargs concurrently, preserving order.

        Stops submitting once the budget is reached; requests not run come
        back as ``{"error": "budget"}``.
        """
        def run(request):
            with self._slots[request["model"]]:
                try:
                    return self.call(**request)
                except BudgetExceeded:
                    return {"text": "", "error": "budget", "cost_usd": 0.0}
        workers = sum(self.concurrency[m] for m in {r["model"] for r in requests}) or 1
        with ThreadPoolExecutor(max_workers=workers) as pool:
            return list(pool.map(run, requests))

    def cached(self, requests: list[dict]) -> int:
        hits = 0
        for r in requests:
            row = self.store.get(
                self.key(r["model"], r["system"], r["user"], r.get("effort"), r.get("tag", ""))
            )
            hits += row is not None and not row.get("error")
        return hits
