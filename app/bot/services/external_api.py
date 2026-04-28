from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class ExternalFactsClient:
    base_url: str
    api_key: str

    def fetch_user_profile(self, user_id: int) -> dict[str, Any]:
        url = f"{self.base_url.rstrip('/')}/users/{user_id}"
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(url=url, headers=headers, method="GET")

        try:
            with urlopen(request, timeout=5) as response:
                payload = response.read().decode("utf-8")
                return cast(dict[str, Any], json.loads(payload))
        except (HTTPError, URLError) as exc:
            raise RuntimeError(f"External API request failed: {exc}") from exc
