from __future__ import annotations

from typing import Any

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential


class GroqClientError(RuntimeError):
    """Raised when the Groq API returns an unrecoverable error."""


class GroqClient:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout_seconds: float,
        retries: int,
        backoff_seconds: float,
    ) -> None:
        self._model = model
        self._http = httpx.AsyncClient(
            base_url=base_url,
            timeout=httpx.Timeout(timeout_seconds),
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
        )
        self._retry = retry(
            reraise=True,
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError, httpx.ReadError)),
            stop=stop_after_attempt(retries + 1),
            wait=wait_exponential(multiplier=backoff_seconds, min=backoff_seconds, max=10),
        )

    async def aclose(self) -> None:
        await self._http.aclose()

    async def generate_reply(self, user_text: str) -> str:
        @self._retry
        async def _call() -> dict[str, Any]:
            response = await self._http.post(
                "/chat/completions",
                json={
                    "model": self._model,
                    "messages": [{"role": "user", "content": user_text}],
                    "temperature": 0.2,
                },
            )
            if response.status_code >= 500:
                response.raise_for_status()
            if response.status_code >= 400:
                raise GroqClientError(f"Groq API rejected request: {response.status_code} {response.text}")
            return response.json()

        try:
            payload = await _call()
        except httpx.HTTPError as exc:
            raise GroqClientError(f"Groq API request failed after retries: {exc}") from exc

        choices = payload.get("choices", [])
        if not choices:
            raise GroqClientError("Groq API returned empty response")
        content = choices[0].get("message", {}).get("content")
        if not content:
            raise GroqClientError("Groq API response missing message content")
        return str(content)
