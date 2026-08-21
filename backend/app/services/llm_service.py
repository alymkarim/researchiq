import logging
from typing import Any

import httpx

from ..config import settings

logger = logging.getLogger(__name__)

PROVIDER_CONFIGS = {
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4.1-mini", "gpt-4.1"],
    },
    "anthropic": {
        "base_url": "https://api.anthropic.com/v1",
        "models": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022"],
    },
    "google": {
        "base_url": "https://generativelanguage.googleapis.com/v1beta",
        "models": ["gemini-2.0-flash", "gemini-2.5-flash"],
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "models": ["llama-3.3-70b-versatile", "mixtral-8x7b-32768"],
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "models": ["meta-llama/Llama-3-70b-chat-hf", "mistralai/Mixtral-8x7B-Instruct-v0.1"],
    },
}


def get_available_providers() -> list[dict[str, Any]]:
    """Get list of available LLM providers and their models."""
    providers = []
    for name, config in PROVIDER_CONFIGS.items():
        providers.append({
            "name": name,
            "base_url": config["base_url"],
            "models": config["models"],
        })
    return providers


async def call_llm(
    messages: list[dict[str, str]],
    model: str | None = None,
    provider: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 2000,
    response_format: dict | None = None,
) -> str:
    """Call LLM with multi-provider support."""
    api_key = settings.llm_api_key
    base_url = settings.llm_base_url
    model = model or settings.llm_model

    if provider and provider in PROVIDER_CONFIGS:
        base_url = PROVIDER_CONFIGS[provider]["base_url"]

    if not api_key:
        raise ValueError("LLM API key not configured.")

    endpoint = f"{base_url.rstrip('/')}/chat/completions"

    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": messages,
    }

    if response_format:
        payload["response_format"] = response_format

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if provider == "anthropic":
        return await _call_anthropic(messages, model, temperature, max_tokens, api_key)

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json=payload,
            )

            if response.status_code in {400, 422} and response_format:
                payload.pop("response_format", None)
                response = await client.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                )

            response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except Exception as exc:
        logger.exception("LLM call failed: %s", exc)
        raise


async def _call_anthropic(
    messages: list[dict[str, str]],
    model: str,
    temperature: float,
    max_tokens: int,
    api_key: str,
) -> str:
    """Call Anthropic's Claude API."""
    system_msg = ""
    user_messages = []

    for msg in messages:
        if msg["role"] == "system":
            system_msg = msg["content"]
        else:
            user_messages.append(msg)

    endpoint = "https://api.anthropic.com/v1/messages"

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": user_messages,
    }

    if system_msg:
        payload["system"] = system_msg

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                endpoint,
                headers=headers,
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        return data["content"][0]["text"]

    except Exception as exc:
        logger.exception("Anthropic call failed: %s", exc)
        raise
