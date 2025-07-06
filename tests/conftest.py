import os
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def mock_env_vars():
    """Мокирование переменных окружения для тестов"""
    env_vars = {
        "BOT_TOKEN": "test_bot_token",
        "OPENAI_API_KEY": "test_openai_api_key",
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
        "REDIS_URL": "redis://localhost:6379/0",
        "OPENAI_MODEL": "gpt-4-turbo-preview",
        "DEFAULT_GENDER": "neutral",
        "MAX_MESSAGE_LENGTH": "4096",
        "CACHE_TTL": "3600",
        "LOG_LEVEL": "INFO",
    }

    with patch.dict(os.environ, env_vars):
        yield


@pytest.fixture
def settings():
    """Фикстура для создания Settings с тестовыми данными"""
    # Импортируем Settings только внутри фикстуры, когда переменные окружения уже установлены
    from config.settings import Settings

    return Settings(
        bot_token="test_bot_token",
        openai_api_key="test_openai_api_key",
        database_url="postgresql://test:test@localhost:5432/test_db",
        redis_url="redis://localhost:6379/0",
        openai_model="gpt-4-turbo-preview",
        default_gender="neutral",
        max_message_length=4096,
        cache_ttl=3600,
        log_level="INFO",
    )
