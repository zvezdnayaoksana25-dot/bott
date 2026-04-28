from __future__ import annotations

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    bot_token: str = Field(alias="BOT_TOKEN")
    groq_api_key: str = Field(alias="GROQ_API_KEY")
    groq_model: str = Field(default="llama-3.1-8b-instant", alias="GROQ_MODEL")
    groq_base_url: str = Field(default="https://api.groq.com/openai/v1", alias="GROQ_BASE_URL")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_format: str = Field(default="json", alias="LOG_FORMAT")

    request_timeout_seconds: float = Field(default=15.0, alias="REQUEST_TIMEOUT_SECONDS", gt=0)
    request_retries: int = Field(default=3, alias="REQUEST_RETRIES", ge=0)
    request_backoff_seconds: float = Field(default=1.0, alias="REQUEST_BACKOFF_SECONDS", ge=0)

    health_host: str = Field(default="0.0.0.0", alias="HEALTH_HOST")
    health_port: int = Field(default=8080, alias="HEALTH_PORT", gt=0, lt=65536)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @field_validator("bot_token", "groq_api_key")
    @classmethod
    def _non_empty_secret(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("must be a non-empty string")
        return cleaned

    @field_validator("log_level")
    @classmethod
    def _log_level_allowed(cls, value: str) -> str:
        allowed = {"CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"}
        normalized = value.upper().strip()
        if normalized not in allowed:
            raise ValueError(f"must be one of: {', '.join(sorted(allowed))}")
        return normalized

    @field_validator("log_format")
    @classmethod
    def _log_format_allowed(cls, value: str) -> str:
        allowed = {"json", "plain"}
        normalized = value.lower().strip()
        if normalized not in allowed:
            raise ValueError(f"must be one of: {', '.join(sorted(allowed))}")
        return normalized


def load_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        details = [f"- {'.'.join(map(str, err['loc']))}: {err['msg']}" for err in exc.errors()]
        formatted = "\n".join(details)
        raise RuntimeError(f"Configuration is invalid. Fix environment variables:\n{formatted}") from exc
