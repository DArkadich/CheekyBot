import pytest
from config.settings import Settings


def test_settings_defaults(settings):
    """Тест значений по умолчанию для настроек"""
    assert settings.bot_token == "test_bot_token"
    assert settings.openai_api_key == "test_openai_api_key"
    assert settings.database_url == "postgresql://test:test@localhost:5432/test_db"
    assert settings.redis_url == "redis://localhost:6379/0"
    assert settings.default_gender == "neutral"
    assert settings.max_message_length == 4096
    assert settings.cache_ttl == 3600
    assert settings.log_level == "INFO"


def test_settings_creation():
    """Тест создания настроек с явными параметрами"""
    test_settings = Settings(
        bot_token="test",
        openai_api_key="test",
        database_url="sqlite:///:memory:",
    )
    
    assert test_settings.bot_token == "test"
    assert test_settings.openai_api_key == "test"
    assert test_settings.database_url == "sqlite:///:memory:"
    assert test_settings.redis_url == "redis://localhost:6379/0"  # значение по умолчанию
    assert test_settings.default_gender == "neutral"  # значение по умолчанию
    assert test_settings.max_message_length == 4096  # значение по умолчанию
    assert test_settings.cache_ttl == 3600  # значение по умолчанию
    assert test_settings.log_level == "INFO"  # значение по умолчанию
