import pytest
from datetime import datetime
from database.models import User, Conversation, UserStats, Gender, CommunicationStyle


class TestModels:
    """Тесты для моделей данных"""

    def test_user_creation(self):
        """Тест создания пользователя"""
        user = User(
            user_id=123456789,
            username="test_user",
            first_name="Test",
            last_name="User",
            gender=Gender.MALE,
            bot_gender=Gender.FEMALE,
            communication_style=CommunicationStyle.PLAYFUL,
            consent_given=True,
            stop_words=["stop", "halt"],
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_active=True,
        )

        assert user.user_id == 123456789
        assert user.username == "test_user"
        assert user.first_name == "Test"
        assert user.gender == Gender.MALE
        assert user.bot_gender == Gender.FEMALE
        assert user.communication_style == CommunicationStyle.PLAYFUL
        assert user.consent_given is True
        assert user.stop_words == ["stop", "halt"]
        assert user.is_active is True

    def test_conversation_creation(self):
        """Тест создания диалога"""
        conversation = Conversation(
            id=1,
            user_id=123456789,
            message="Привет!",
            bot_response="Привет! Как дела?",
            communication_style=CommunicationStyle.PLAYFUL,
            tokens_used=10,
            created_at=datetime.now(),
        )

        assert conversation.id == 1
        assert conversation.user_id == 123456789
        assert conversation.message == "Привет!"
        assert conversation.bot_response == "Привет! Как дела?"
        assert conversation.communication_style == CommunicationStyle.PLAYFUL
        assert conversation.tokens_used == 10

    def test_user_stats_creation(self):
        """Тест создания статистики пользователя"""
        stats = UserStats(
            user_id=123456789,
            total_messages=100,
            total_tokens=5000,
            favorite_style=CommunicationStyle.ROMANTIC,
            last_activity=datetime.now(),
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        assert stats.user_id == 123456789
        assert stats.total_messages == 100
        assert stats.total_tokens == 5000
        assert stats.favorite_style == CommunicationStyle.ROMANTIC
