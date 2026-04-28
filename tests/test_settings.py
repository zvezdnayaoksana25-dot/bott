import os

import pytest

from config.settings import load_settings


@pytest.fixture(autouse=True)
def _clear_env():
    keys = [
        "BOT_TOKEN",
        "GROQ_API_KEY",
        "GROQ_MODEL",
        "GROQ_BASE_URL",
        "LOG_LEVEL",
        "LOG_FORMAT",
        "REQUEST_TIMEOUT_SECONDS",
        "REQUEST_RETRIES",
        "REQUEST_BACKOFF_SECONDS",
        "HEALTH_HOST",
        "HEALTH_PORT",
    ]
    snapshot = {k: os.environ.get(k) for k in keys}
    for k in keys:
        os.environ.pop(k, None)
    yield
    for k, v in snapshot.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v


def test_load_settings_success():
    os.environ["BOT_TOKEN"] = "token"
    os.environ["GROQ_API_KEY"] = "key"

    settings = load_settings()

    assert settings.bot_token == "token"
    assert settings.groq_api_key == "key"


def test_load_settings_validation_error():
    with pytest.raises(RuntimeError) as exc:
        load_settings()

    assert "Configuration is invalid" in str(exc.value)
