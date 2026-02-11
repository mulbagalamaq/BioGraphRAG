"""Async Groq LLM client."""

from __future__ import annotations

import logging

import httpx

from backend.config import AppConfig

LOGGER = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the LLM API call fails."""


async def call_llm(prompt: str, config: AppConfig) -> str:
    """Send *prompt* to Groq and return the assistant response text."""
    api_key = config.get("llm.api_key", "")
    if not api_key or api_key.startswith("${"):
        raise LLMError("GROQ_API_KEY is not configured")

    api_url = config.get("llm.api_url", "https://api.groq.com/openai/v1/chat/completions")
    model = config.get("llm.model", "llama-3.1-8b-instant")
    temperature = float(config.get("llm.temperature", 0.2))
    max_tokens = int(config.get("llm.max_tokens", 512))

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(api_url, json=payload, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as exc:
            LOGGER.error("Groq API HTTP %s: %s", exc.response.status_code, exc.response.text[:300])
            raise LLMError(f"Groq API returned {exc.response.status_code}") from exc
        except Exception as exc:
            LOGGER.error("LLM call failed: %s", exc)
            raise LLMError(str(exc)) from exc
