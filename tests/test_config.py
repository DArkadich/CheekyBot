import pytest

@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "test")
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("DEFAULT_GENDER", "neutral")
    monkeypatch.setenv("MAX_MESSAGE_LENGTH", "4096")
    monkeypatch.setenv("CACHE_TTL", "3600")
    monkeypatch.setenv("LOG_LEVEL", "INFO")


def test_settings_load():
    from config.settings import Settings
    settings = Settings()
    assert settings.bot_token == "test"
    assert settings.openai_api_key == "test"
    assert settings.database_url == "sqlite:///:memory:"
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.default_gender == "neutral"
    assert settings.max_message_length == 4096
    assert settings.cache_ttl == 3600
    assert settings.log_level == "INFO"
