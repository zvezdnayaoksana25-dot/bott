from __future__ import annotations

import json
from typing import Any
from unittest.mock import patch

from bot.services.external_api import ExternalFactsClient


class FakeHTTPResponse:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._payload

    def __enter__(self) -> "FakeHTTPResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None


def test_fetch_user_profile_with_mocked_api() -> None:
    def fake_urlopen(request: Any, timeout: int) -> FakeHTTPResponse:
        assert request.full_url.endswith("/users/42")
        assert request.headers.get("Authorization") == "Bearer test-key"
        assert timeout == 5
        return FakeHTTPResponse({"id": 42, "name": "Alex"})

    client = ExternalFactsClient(base_url="https://mocked.example.test", api_key="test-key")
    with patch("bot.services.external_api.urlopen", side_effect=fake_urlopen):
        profile = client.fetch_user_profile(42)

    assert profile == {"id": 42, "name": "Alex"}
