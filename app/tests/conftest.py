from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest


@pytest.fixture
def sample_update() -> dict[str, Any]:
    fixture_path = Path(__file__).parent / "fixtures" / "sample_update.json"
    with fixture_path.open("r", encoding="utf-8") as fh:
        return dict(json.load(fh))


@pytest.fixture
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("EXTERNAL_API_BASE_URL", raising=False)
    monkeypatch.setenv("APP_ENV_FILE", ".env.test")
