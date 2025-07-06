import hashlib
import json
from typing import Any, Dict, List, Optional

import openai
import redis
from loguru import logger

from config.settings import Settings, settings
from database.models import CommunicationStyle, Gender


class OpenAIService:
    def __init__(self) -> None:
        # Используем settings или создаем новый экземпляр
        if settings is None:
            # В тестах или CI/CD создаем с дефолтными значениями
            self.settings: Settings = Settings(
                bot_token="dummy_token",
                openai_api_key="dummy_key",
                database_url="dummy_url",
                redis_url="redis://localhost:6379/0",
                openai_model="gpt-4-turbo-preview",
            )
        else:
            self.settings = settings

        self.client = openai.AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.redis_client = redis.from_url(self.settings.redis_url)
        self.model = self.settings.openai_model

    def _generate_cache_key(
        self,
        message: str,
        style: CommunicationStyle,
        user_gender: Gender,
        bot_gender: Gender,
    ) -> str:
        """Генерация ключа кеша для запроса"""
        content = f"{message}:{style.value}:{user_gender.value}:{bot_gender.value}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_style_prompt(
        self, style: CommunicationStyle, user_gender: Gender, bot_gender: Gender
    ) -> str:
        """Получение промпта для стиля общения"""
        base_prompts = {
            CommunicationStyle.PLAYFUL: {
                Gender.MALE: "Ты игривый и кокетливый парень, который любит флиртовать и подшучивать. Используй эмодзи, шутки и легкие намеки.",
                Gender.FEMALE: "Ты игривая и кокетливая девушка, которая любит флиртовать и подшучивать. Используй эмодзи, шутки и легкие намеки.",
                Gender.NEUTRAL: "Ты игривый и кокетливый собеседник, который любит флиртовать и подшучивать. Используй эмодзи, шутки и легкие намеки.",
            },
            CommunicationStyle.ROMANTIC: {
                Gender.MALE: "Ты романтичный и нежный парень, который говорит красиво и поэтично. Используй романтичные комплименты и нежные слова.",
                Gender.FEMALE: "Ты романтичная и нежная девушка, которая говорит красиво и поэтично. Используй романтичные комплименты и нежные слова.",
                Gender.NEUTRAL: "Ты романтичный и нежный собеседник, который говорит красиво и поэтично. Используй романтичные комплименты и нежные слова.",
            },
            CommunicationStyle.PASSIONATE: {
                Gender.MALE: "Ты страстный и темпераментный парень, который выражает эмоции ярко и откровенно. Можешь использовать более смелые выражения.",
                Gender.FEMALE: "Ты страстная и темпераментная девушка, которая выражает эмоции ярко и откровенно. Можешь использовать более смелые выражения.",
                Gender.NEUTRAL: "Ты страстный и темпераментный собеседник, который выражает эмоции ярко и откровенно. Можешь использовать более смелые выражения.",
            },
            CommunicationStyle.MYSTERIOUS: {
                Gender.MALE: "Ты загадочный и интригующий парень, который говорит намеками и создает интригу. Используй таинственные фразы и недоговоренности.",
                Gender.FEMALE: "Ты загадочная и интригующая девушка, которая говорит намеками и создает интригу. Используй таинственные фразы и недоговоренности.",
                Gender.NEUTRAL: "Ты загадочный и интригующий собеседник, который говорит намеками и создает интригу. Используй таинственные фразы и недоговоренности.",
            },
        }

        return base_prompts[style][bot_gender]

    async def generate_response(
        self,
        message: str,
        style: CommunicationStyle,
        user_gender: Gender,
        bot_gender: Gender,
        stop_words: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Генерация ответа с использованием OpenAI API"""

        # Проверка стоп-слов
        if stop_words:
            message_lower = message.lower()
            for word in stop_words:
                if word.lower() in message_lower:
                    return "Извини, но я не могу ответить на это сообщение."

        # Проверка кеша
        cache_key = self._generate_cache_key(message, style, user_gender, bot_gender)
        cached_response = self.redis_client.get(cache_key)

        if cached_response:
            logger.info(f"Using cached response for message: {message[:50]}...")
            decoded = cached_response.decode("utf-8")
            return decoded if isinstance(decoded, str) else None

        try:
            system_prompt = self._get_style_prompt(style, user_gender, bot_gender)

            # Добавление правил безопасности
            safety_prompt = """
            Важные правила:
            1. Всегда уважай границы собеседника
            2. Не используй оскорбительные или агрессивные выражения
            3. Если собеседник просит остановиться - немедленно прекращай
            4. Помни о возрасте собеседника (18+)
            5. Не используй нецензурную лексику без явного согласия
            6. Будь игривым, но не навязчивым
            """

            full_system_prompt = f"{system_prompt}\n\n{safety_prompt}"

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": full_system_prompt},
                    {"role": "user", "content": message},
                ],
                max_tokens=500,
                temperature=0.8,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            bot_response = response.choices[0].message.content
            if bot_response is not None:
                bot_response = bot_response.strip()
            else:
                return None

            # Сохранение в кеш
            self.redis_client.setex(cache_key, self.settings.cache_ttl, bot_response)

            logger.info(f"Generated response for message: {message[:50]}...")
            return bot_response

        except openai.RateLimitError:
            logger.error("OpenAI API rate limit exceeded")
            rate_limit_msg: str = (
                "Извини, сейчас слишком много запросов. Попробуй через минуту."
            )
            return rate_limit_msg

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            api_error_msg: str = (
                "Извини, произошла ошибка при обработке твоего сообщения."
            )
            return api_error_msg

        except Exception as e:
            logger.error(f"Unexpected error in OpenAI service: {e}")
            general_error_msg: str = "Извини, что-то пошло не так. Попробуй еще раз."
            return general_error_msg

    async def generate_roleplay_scenario(
        self, scenario_type: str, user_gender: Gender, bot_gender: Gender
    ) -> Optional[str]:
        """Генерация ролевого сценария"""
        try:
            scenarios = {
                "romantic_date": "Романтическое свидание в красивом ресторане",
                "beach_romance": "Романтическая прогулка по пляжу на закате",
                "mountain_adventure": "Приключение в горах с красивыми видами",
                "city_exploration": "Исследование города и его достопримечательностей",
                "cozy_home": "Уютный вечер дома с камином и вином",
            }

            scenario_description = scenarios.get(
                scenario_type, "Романтическое свидание"
            )

            system_prompt = f"""
            Ты создаешь ролевой сценарий для флирта и романтического общения.
            Сценарий: {scenario_description}
            Твой пол: {bot_gender.value}
            Пол собеседника: {user_gender.value}
            
            Создай краткое описание сценария (2-3 предложения) и начни диалог.
            Будь игривым, романтичным и вовлекающим.
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Начни ролевую игру"},
                ],
                max_tokens=300,
                temperature=0.9,
            )

            content = response.choices[0].message.content
            if content is not None:
                return content.strip()
            else:
                return None

        except Exception as e:
            logger.error(f"Error generating roleplay scenario: {e}")
            scenario_error_msg: str = (
                "Извини, не удалось создать сценарий. Попробуй еще раз."
            )
            return scenario_error_msg


# Глобальный экземпляр сервиса OpenAI
openai_service = OpenAIService()
