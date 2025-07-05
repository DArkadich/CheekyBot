import pytest
from unittest.mock import patch
from config.settings import Settings, Gender, CommunicationStyle


class TestSettings:
    """Тесты для настроек приложения"""

    def test_gender_enum(self):
        """Тест перечисления Gender"""
        assert Gender.MALE.value == "male"
        assert Gender.FEMALE.value == "female"
        assert Gender.NEUTRAL.value == "neutral"

    def test_communication_style_enum(self):
        """Тест перечисления CommunicationStyle"""
        assert CommunicationStyle.PLAYFUL.value == "playful"
        assert CommunicationStyle.ROMANTIC.value == "romantic"
        assert CommunicationStyle.PASSIONATE.value == "passionate"
        assert CommunicationStyle.MYSTERIOUS.value == "mysterious"

    @patch.dict('os.environ', {
        'BOT_TOKEN': 'test_token',
        'OPENAI_API_KEY': 'test_openai_key',
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/test'
    })
    def test_settings_creation(self):
        """Тест создания настроек"""
        settings = Settings()
        assert settings.bot_token == 'test_token'
        assert settings.openai_api_key == 'test_openai_key'
        assert settings.database_url == 'postgresql://test:test@localhost:5432/test'
        assert settings.default_gender == Gender.NEUTRAL
        assert settings.max_message_length == 4096
        assert settings.cache_ttl == 3600
        assert settings.log_level == "INFO" 