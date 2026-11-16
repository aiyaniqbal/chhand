"""Asynchronous HTTP client for OpenAI-compatible LLM endpoints."""

import json
from typing import Any

import httpx

from app.config import settings
from app.errors import LLMConfigurationError, LLMProviderError, LLMTimeoutError


class LLMClient:
    """Async client interacting with OpenAI-compatible chat completion APIs."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        model: str | None = None,
        timeout_seconds: float | None = None,
    ):
        self.api_key = api_key if api_key is not None else settings.LLM_API_KEY
        self.base_url = (base_url or settings.LLM_BASE_URL).rstrip("/")
        self.model = model or settings.LLM_MODEL
        self.timeout_seconds = timeout_seconds or settings.LLM_TIMEOUT_SECONDS

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def generate_chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 800,
    ) -> str:
        """Sends chat completion request to the LLM provider."""
        if not self.is_configured:
            raise LLMConfigurationError(
                "LLM API key is not configured. Set LLM_API_KEY in .env to enable AI rewriting."
            )

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "response_format": {"type": "json_object"},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(endpoint, headers=headers, json=payload)
                if response.status_code != 200:
                    raise LLMProviderError(
                        f"LLM API returned HTTP {response.status_code}: {response.text[:200]}"
                    )
                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    raise LLMProviderError("LLM response did not contain any choices.")
                return choices[0]["message"]["content"]
        except httpx.TimeoutException as exc:
            raise LLMTimeoutError(
                f"LLM request timed out after {self.timeout_seconds} seconds."
            ) from exc
        except (httpx.ConnectError, httpx.RequestError) as exc:
            raise LLMProviderError(f"Failed to connect to LLM endpoint: {exc}") from exc

    async def generate_json(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
    ) -> dict[str, Any]:
        """Generates structured JSON from the LLM."""
        raw_text = await self.generate_chat_completion(messages, temperature=temperature)
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            # Fallback if markdown json fence exists
            cleaned = raw_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            elif cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            return json.loads(cleaned.strip())
