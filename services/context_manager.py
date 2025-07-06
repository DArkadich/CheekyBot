"""
Сервис для управления контекстом диалогов с оптимизацией для масштабирования
"""
import hashlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import redis
from loguru import logger

from config.settings import settings
from database.models import Conversation


class ContextManager:
    """Менеджер контекста диалогов с многоуровневым кешированием"""

    def __init__(self) -> None:
        self.redis_client = redis.from_url(settings.redis_url)
        self.context_ttl = 3600  # 1 час для активного контекста
        self.summary_ttl = 86400 * 7  # 7 дней для сводок

    def _get_context_key(self, user_id: int) -> str:
        """Генерация ключа для контекста пользователя"""
        return f"context:{user_id}"

    def _get_summary_key(self, user_id: int) -> str:
        """Генерация ключа для сводки контекста"""
        return f"summary:{user_id}"

    def _get_session_key(self, user_id: int) -> str:
        """Генерация ключа для активной сессии"""
        return f"session:{user_id}"

    async def add_message_to_context(
        self, user_id: int, message: str, bot_response: str, communication_style: str
    ) -> None:
        """Добавление сообщения в контекст с оптимизацией"""

        # Получаем текущий контекст
        context = await self.get_context(user_id)

        # Добавляем новое сообщение
        context.append(
            {
                "role": "user",
                "content": message,
                "timestamp": datetime.now().isoformat(),
            }
        )
        context.append(
            {
                "role": "assistant",
                "content": bot_response,
                "timestamp": datetime.now().isoformat(),
            }
        )

        # Ограничиваем размер контекста (последние 20 сообщений)
        if len(context) > 20:
            context = context[-20:]

        # Сохраняем в Redis
        await self._save_context(user_id, context)

        # Обновляем сводку каждые 10 сообщений
        if len(context) % 10 == 0:
            await self._update_summary(user_id, context)

    async def get_context(
        self, user_id: int, max_messages: int = 10
    ) -> List[Dict[str, str]]:
        """Получение контекста с оптимизацией"""

        # Сначала пробуем получить из Redis
        context_key = self._get_context_key(user_id)
        cached_context = self.redis_client.get(context_key)

        if cached_context:
            context = json.loads(cached_context)
            # Возвращаем только последние max_messages
            return context[-max_messages * 2 :]  # *2 потому что user + assistant

        # Если нет в кеше, возвращаем пустой контекст
        return []

    async def get_optimized_context(
        self, user_id: int, max_tokens: int = 1000
    ) -> List[Dict[str, str]]:
        """Получение оптимизированного контекста с учетом лимита токенов"""

        context = await self.get_context(user_id, max_messages=20)

        if not context:
            return []

        # Если контекст слишком большой, используем сводку
        total_tokens = sum(len(msg["content"].split()) for msg in context)

        if total_tokens > max_tokens:
            summary = await self.get_summary(user_id)
            if summary:
                return [{"role": "system", "content": summary}]
            else:
                # Возвращаем только последние сообщения
                return context[-4:]  # Последние 2 пары сообщений

        return context

    async def get_summary(self, user_id: int) -> Optional[str]:
        """Получение сводки контекста"""
        summary_key = self._get_summary_key(user_id)
        cached_summary = self.redis_client.get(summary_key)

        if cached_summary:
            return cached_summary.decode("utf-8")

        return None

    async def _save_context(self, user_id: int, context: List[Dict]) -> None:
        """Сохранение контекста в Redis"""
        context_key = self._get_context_key(user_id)
        self.redis_client.setex(
            context_key, self.context_ttl, json.dumps(context, ensure_ascii=False)
        )

    async def _update_summary(self, user_id: int, context: List[Dict]) -> None:
        """Обновление сводки контекста"""
        if len(context) < 10:
            return

        # Создаем сводку на основе последних сообщений
        recent_messages = context[-10:]
        summary = self._create_summary(recent_messages)

        if summary:
            summary_key = self._get_summary_key(user_id)
            self.redis_client.setex(summary_key, self.summary_ttl, summary)

    def _create_summary(self, messages: List[Dict]) -> str:
        """Создание сводки контекста"""
        if not messages:
            return ""

        # Извлекаем ключевые темы и настроения
        topics = []
        mood = "нейтральное"

        for msg in messages:
            content = msg["content"].lower()

            # Простой анализ тем
            if any(word in content for word in ["работа", "карьера", "бизнес"]):
                topics.append("работа")
            elif any(word in content for word in ["путешествие", "поездка", "отпуск"]):
                topics.append("путешествия")
            elif any(word in content for word in ["музыка", "фильм", "книга"]):
                topics.append("развлечения")
            elif any(word in content for word in ["спорт", "фитнес", "тренировка"]):
                topics.append("спорт")

            # Анализ настроения
            if any(word in content for word in ["😊", "😄", "радость", "весело"]):
                mood = "радостное"
            elif any(word in content for word in ["😢", "грусть", "печаль"]):
                mood = "грустное"
            elif any(word in content for word in ["😍", "любовь", "романтика"]):
                mood = "романтичное"

        # Создаем сводку
        unique_topics = list(set(topics))[:3]  # Максимум 3 темы
        topics_str = ", ".join(unique_topics) if unique_topics else "общие темы"

        return f"Контекст разговора: {topics_str}. Настроение: {mood}. Продолжай в том же стиле."

    async def clear_context(self, user_id: int) -> None:
        """Очистка контекста пользователя"""
        context_key = self._get_context_key(user_id)
        summary_key = self._get_summary_key(user_id)
        session_key = self._get_session_key(user_id)

        self.redis_client.delete(context_key, summary_key, session_key)

    async def get_user_preferences(self, user_id: int) -> Dict[str, str]:
        """Получение предпочтений пользователя из контекста"""
        context = await self.get_context(user_id, max_messages=50)

        preferences = {
            "topics": [],
            "communication_style": "neutral",
            "mood": "neutral",
        }

        if not context:
            return preferences

        # Анализируем контекст для извлечения предпочтений
        all_content = " ".join([msg["content"] for msg in context])

        # Определяем стиль общения
        if any(word in all_content.lower() for word in ["шутка", "игра", "весело"]):
            preferences["communication_style"] = "playful"
        elif any(
            word in all_content.lower() for word in ["романтика", "любовь", "нежность"]
        ):
            preferences["communication_style"] = "romantic"
        elif any(
            word in all_content.lower() for word in ["страсть", "эмоции", "чувства"]
        ):
            preferences["communication_style"] = "passionate"

        return preferences


# Глобальный экземпляр менеджера контекста
context_manager = ContextManager()
