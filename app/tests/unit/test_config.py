from bot.config import Settings


def test_settings_can_load_empty_keys(clean_env: None) -> None:
    settings = Settings.from_env()
    assert settings.telegram_token == ""
    assert settings.groq_api_key == ""
    assert settings.external_api_base_url == "https://mocked.example.test"
