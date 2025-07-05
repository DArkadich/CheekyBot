import asyncpg
from typing import Optional, List, Dict, Any
from loguru import logger
from config.settings import settings
from database.models import (
    User,
    Conversation,
    UserStats,
    Gender,
    CommunicationStyle,
    CREATE_TABLES_SQL,
)


class DatabaseManager:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        """Создание пула соединений с базой данных"""
        try:
            self.pool = await asyncpg.create_pool(
                settings.database_url, min_size=5, max_size=20, command_timeout=60
            )
            logger.info("Database connection pool created successfully")

            # Создание таблиц при первом подключении
            async with self.pool.acquire() as conn:
                await conn.execute(CREATE_TABLES_SQL)
                logger.info("Database tables created/verified")

        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    async def close(self):
        """Закрытие пула соединений"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    async def get_user(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT user_id, username, first_name, last_name, gender, bot_gender,
                       communication_style, consent_given, stop_words, created_at, updated_at, is_active
                FROM users WHERE user_id = $1
                """,
                user_id,
            )

            if row:
                return User(
                    user_id=row["user_id"],
                    username=row["username"],
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    gender=Gender(row["gender"]),
                    bot_gender=Gender(row["bot_gender"]),
                    communication_style=CommunicationStyle(row["communication_style"]),
                    consent_given=row["consent_given"],
                    stop_words=row["stop_words"] or [],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    is_active=row["is_active"],
                )
            return None

    async def create_user(self, user: User) -> User:
        """Создание нового пользователя"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO users (user_id, username, first_name, last_name, gender, bot_gender,
                                 communication_style, consent_given, stop_words)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """,
                user.user_id,
                user.username,
                user.first_name,
                user.last_name,
                user.gender.value,
                user.bot_gender.value,
                user.communication_style.value,
                user.consent_given,
                user.stop_words,
            )

            # Создание записи статистики
            await conn.execute(
                """
                INSERT INTO user_stats (user_id) VALUES ($1)
                """,
                user.user_id,
            )

            logger.info(f"Created new user: {user.user_id}")
            return user

    async def update_user(self, user: User) -> User:
        """Обновление данных пользователя"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE users SET username = $2, first_name = $3, last_name = $4,
                                gender = $5, bot_gender = $6, communication_style = $7,
                                consent_given = $8, stop_words = $9, updated_at = NOW()
                WHERE user_id = $1
                """,
                user.user_id,
                user.username,
                user.first_name,
                user.last_name,
                user.gender.value,
                user.bot_gender.value,
                user.communication_style.value,
                user.consent_given,
                user.stop_words,
            )
            return user

    async def save_conversation(self, conversation: Conversation) -> Conversation:
        """Сохранение диалога"""
        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO conversations (user_id, message, bot_response, communication_style, tokens_used)
                VALUES ($1, $2, $3, $4, $5)
                """,
                conversation.user_id,
                conversation.message,
                conversation.bot_response,
                conversation.communication_style.value,
                conversation.tokens_used,
            )

            # Обновление статистики пользователя
            await conn.execute(
                """
                UPDATE user_stats SET total_messages = total_messages + 1,
                                    total_tokens = total_tokens + $2,
                                    last_activity = NOW(),
                                    updated_at = NOW()
                WHERE user_id = $1
                """,
                conversation.user_id,
                conversation.tokens_used,
            )

            return conversation

    async def get_user_stats(self, user_id: int) -> Optional[UserStats]:
        """Получение статистики пользователя"""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT user_id, total_messages, total_tokens, favorite_style,
                       last_activity, created_at, updated_at
                FROM user_stats WHERE user_id = $1
                """,
                user_id,
            )

            if row:
                return UserStats(
                    user_id=row["user_id"],
                    total_messages=row["total_messages"],
                    total_tokens=row["total_tokens"],
                    favorite_style=CommunicationStyle(row["favorite_style"]),
                    last_activity=row["last_activity"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
            return None

    async def get_recent_conversations(
        self, user_id: int, limit: int = 10
    ) -> List[Conversation]:
        """Получение последних диалогов пользователя"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, user_id, message, bot_response, communication_style, tokens_used, created_at
                FROM conversations WHERE user_id = $1
                ORDER BY created_at DESC LIMIT $2
                """,
                user_id,
                limit,
            )

            return [
                Conversation(
                    id=row["id"],
                    user_id=row["user_id"],
                    message=row["message"],
                    bot_response=row["bot_response"],
                    communication_style=CommunicationStyle(row["communication_style"]),
                    tokens_used=row["tokens_used"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]


# Глобальный экземпляр менеджера базы данных
db = DatabaseManager()
