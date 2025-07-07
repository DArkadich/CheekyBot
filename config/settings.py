from enum import Enum
from typing import Optional

from pydantic_settings import BaseSettings


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class CommunicationStyle(str, Enum):
    PLAYFUL = "playful"
    ROMANTIC = "romantic"
    PASSIONATE = "passionate"
    MYSTERIOUS = "mysterious"


class Settings(BaseSettings):
    # Telegram Bot Configuration
    bot_token: str

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4-turbo-preview"

    # Database Configuration
    database_url: str

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"

    # Bot Settings
    default_gender: Gender = Gender.NEUTRAL
    max_message_length: int = 4096
    cache_ttl: int = 3600

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance - создаем только если переменные окружения доступны
settings: Optional[Settings] = None

try:
    settings = Settings()
except Exception:
    # В тестах или CI/CD переменные окружения могут отсутствовать
    pass
 