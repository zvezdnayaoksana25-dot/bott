from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _load_env_file(path: str) -> None:
    env_path = Path(path)
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


@dataclass(frozen=True)
class Settings:
    telegram_token: str
    groq_api_key: str
    external_api_base_url: str

    @classmethod
    def from_env(cls) -> "Settings":
        env_file = os.getenv("APP_ENV_FILE", ".env")
        _load_env_file(env_file)
        return cls(
            telegram_token=os.getenv("TELEGRAM_TOKEN", ""),
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            external_api_base_url=os.getenv("EXTERNAL_API_BASE_URL", "https://example.invalid"),
        )
