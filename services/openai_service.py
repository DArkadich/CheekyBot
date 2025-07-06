import hashlib
import json
from typing import Any, Dict, List, Optional, cast

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
        """Получение промпта для стиля общения с правильной персонализацией"""

        # Определяем роли бота в зависимости от его пола
        gender_roles = {
            Gender.MALE: {
                CommunicationStyle.PLAYFUL: "игривый и кокетливый парень",
                CommunicationStyle.ROMANTIC: "романтичный и нежный парень",
                CommunicationStyle.PASSIONATE: "страстный и темпераментный парень",
                CommunicationStyle.MYSTERIOUS: "загадочный и интригующий парень",
            },
            Gender.FEMALE: {
                CommunicationStyle.PLAYFUL: "игривая и кокетливая девушка",
                CommunicationStyle.ROMANTIC: "романтичная и нежная девушка",
                CommunicationStyle.PASSIONATE: "страстная и темпераментная девушка",
                CommunicationStyle.MYSTERIOUS: "загадочная и интригующая девушка",
            },
        }

        # Определяем стилевые особенности для каждого стиля
        style_details = {
            CommunicationStyle.PLAYFUL: {
                "tone": "игривый и веселый",
                "emoji": "😊 😉 😋 🎭",
                "approach": "используй шутки, легкие намеки и игривые комплименты",
                "examples": "подмигивания, игривые вопросы, веселые истории",
            },
            CommunicationStyle.ROMANTIC: {
                "tone": "нежный и поэтичный",
                "emoji": "💕 🌹 ✨ 💫",
                "approach": "говори красиво, используй романтичные комплименты и поэтические выражения",
                "examples": "поэтические сравнения, романтичные комплименты, нежные слова",
            },
            CommunicationStyle.PASSIONATE: {
                "tone": "страстный и эмоциональный",
                "emoji": "🔥 💋 😍 💖",
                "approach": "выражай эмоции ярко и откровенно, будь смелым в выражениях",
                "examples": "страстные комплименты, смелые намеки, яркие эмоции",
            },
            CommunicationStyle.MYSTERIOUS: {
                "tone": "загадочный и интригующий",
                "emoji": "😏 🕵️ 🌙 ✨",
                "approach": "говори намеками, создавай интригу и загадочность",
                "examples": "загадочные намеки, интригующие вопросы, таинственные истории",
            },
        }

        # Определяем адаптацию под пол собеседника
        gender_adaptation = {
            Gender.MALE: {
                Gender.MALE: "Твой собеседник - парень. Адаптируй стиль под мужское общение, можешь использовать мужские шутки и темы.",
                Gender.FEMALE: "Твой собеседник - девушка. Будь галантным и внимательным, используй комплименты и романтичные выражения.",
            },
            Gender.FEMALE: {
                Gender.MALE: "Твой собеседник - парень. Будь кокетливой, но нежной, используй женские хитрости и обаяние.",
                Gender.FEMALE: "Твой собеседник - девушка. Создай атмосферу женской дружбы с элементами флирта и взаимопонимания.",
            },
        }

        bot_role = gender_roles[bot_gender][style]
        style_detail = style_details[style]
        gender_adapt = gender_adaptation[bot_gender][user_gender]

        prompt = f"""
        Ты {bot_role}. {gender_adapt}
        
        СТИЛЬ ОБЩЕНИЯ:
        - Тон: {style_detail['tone']}
        - Подход: {style_detail['approach']}
        - Эмодзи: {style_detail['emoji']}
        - Примеры: {style_detail['examples']}
        
        ВАЖНО: ВСЕГДА помни свой пол ({bot_gender.value}) и пол собеседника ({user_gender.value}). 
        Адаптируй каждое сообщение под эту комбинацию полов.
        """

        return prompt

    async def generate_response(
        self,
        message: str,
        style: CommunicationStyle,
        user_gender: Gender,
        bot_gender: Gender,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        stop_words: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Генерация ответа с использованием OpenAI API и контекстной памяти"""

        # Проверка стоп-слов
        if stop_words:
            message_lower = message.lower()
            for word in stop_words:
                if word.lower() in message_lower:
                    return "Извини, но я не могу ответить на это сообщение."

        # Проверка кеша (только для одиночных сообщений без истории)
        if not conversation_history:
            cache_key = self._generate_cache_key(
                message, style, user_gender, bot_gender
            )
            cached_response = self.redis_client.get(cache_key)

            if cached_response:
                logger.info(f"Using cached response for message: {message[:50]}...")
                decoded = cached_response.decode("utf-8")
                return decoded if isinstance(decoded, str) else None

        try:
            system_prompt = self._get_style_prompt(style, user_gender, bot_gender)

            # Добавление правил безопасности и контекста
            safety_prompt = """
            ВАЖНЫЕ ПРАВИЛА ОБЩЕНИЯ:
            
            1. КОНТЕКСТ И ПОСЛЕДОВАТЕЛЬНОСТЬ:
               - ВСЕГДА помни пол собеседника и адаптируй стиль общения
               - Поддерживай контекст предыдущих сообщений
               - Отвечай на конкретные вопросы и реплики собеседника
               - Не перескакивай с темы на тему без логической связи
               - Используй информацию из предыдущих сообщений для персонализации
            
            2. ПЕРСОНАЛИЗАЦИЯ:
               - Используй информацию о поле собеседника в каждом ответе
               - Адаптируй комплименты и выражения под пол собеседника
               - Не путай полы - если собеседник парень, обращайся как к парню
               - Запоминай предпочтения и интересы собеседника из диалога
            
            3. БЕЗОПАСНОСТЬ:
               - Всегда уважай границы собеседника
               - Не используй оскорбительные или агрессивные выражения
               - Если собеседник просит остановиться - немедленно прекращай
               - Помни о возрасте собеседника (18+)
               - Не используй нецензурную лексику без явного согласия
            
            4. СТИЛЬ ОБЩЕНИЯ:
               - Будь игривым, но не навязчивым
               - Поддерживай выбранный стиль общения на протяжении всей беседы
               - Используй эмодзи для выражения эмоций
               - Отвечай естественно и непринужденно
               - Поддерживай эмоциональную связь с собеседником
            """

            full_system_prompt = f"{system_prompt}\n\n{safety_prompt}"

            # Формируем сообщения для API
            messages = [{"role": "system", "content": full_system_prompt}]

            # Добавляем историю диалога (последние 10 сообщений для экономии токенов)
            if conversation_history:
                recent_history = conversation_history[-10:]  # Последние 10 сообщений
                for msg in recent_history:
                    messages.append(
                        {
                            "role": msg.get("role", "user"),
                            "content": msg.get("content", ""),
                        }
                    )

            # Добавляем текущее сообщение
            messages.append({"role": "user", "content": message})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type: ignore[arg-type]
                max_tokens=500,
                temperature=0.8,
                presence_penalty=0.1,
                frequency_penalty=0.1,
            )

            bot_response = response.choices[0].message.content
            if bot_response is not None and isinstance(bot_response, str):
                return cast(Optional[str], bot_response.strip())
            else:
                return None

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
        """Генерация ролевого сценария с детальными описаниями"""
        try:
            # Детальные сценарии с настройками
            scenarios = {
                "romantic_date": {
                    "title": "Романтическое свидание",
                    "setting": "Элегантный ресторан при свечах с видом на город",
                    "mood": "романтичный и интимный",
                    "activities": [
                        "ужин при свечах",
                        "танцы",
                        "прогулка по набережной",
                    ],
                    "dialogue_starters": [
                        "Какой у тебя любимый ресторан?",
                        "Ты часто ходишь на свидания?",
                        "Что для тебя идеальное свидание?",
                    ],
                    "atmosphere": "мягкий свет свечей, тихая музыка, аромат цветов",
                },
                "beach_romance": {
                    "title": "Романтика на пляже",
                    "setting": "Уединенный пляж на закате солнца",
                    "mood": "расслабленный и романтичный",
                    "activities": ["прогулка по пляжу", "купание", "пикник"],
                    "dialogue_starters": [
                        "Ты любишь море?",
                        "Какой твой любимый пляж?",
                        "Что ты думаешь о закатах?",
                    ],
                    "atmosphere": "шум волн, теплый песок, золотистый закат",
                },
                "mountain_adventure": {
                    "title": "Приключение в горах",
                    "setting": "Живописная горная тропа с панорамными видами",
                    "mood": "приключенческий и воодушевляющий",
                    "activities": ["поход", "фотографирование", "привал с видом"],
                    "dialogue_starters": [
                        "Ты любишь активный отдых?",
                        "Бывал ли ты в горах?",
                        "Что тебя больше всего впечатляет в природе?",
                    ],
                    "atmosphere": "свежий горный воздух, величественные вершины, тишина",
                },
                "city_exploration": {
                    "title": "Исследование города",
                    "setting": "Исторический центр города с уютными улочками",
                    "mood": "любознательный и веселый",
                    "activities": [
                        "прогулка по достопримечательностям",
                        "посещение кафе",
                        "шоппинг",
                    ],
                    "dialogue_starters": [
                        "Ты любишь путешествовать?",
                        "Какой город тебе больше всего нравится?",
                        "Что тебя привлекает в новых местах?",
                    ],
                    "atmosphere": "оживленные улицы, архитектурные красоты, местный колорит",
                },
                "cozy_home": {
                    "title": "Уютный вечер дома",
                    "setting": "Уютная гостиная с камином и мягким освещением",
                    "mood": "домашний и интимный",
                    "activities": ["вечер у камина", "просмотр фильма", "игры"],
                    "dialogue_starters": [
                        "Ты любишь домашние вечера?",
                        "Какой твой любимый фильм?",
                        "Что для тебя идеальный вечер дома?",
                    ],
                    "atmosphere": "тепло камина, мягкие подушки, приятная музыка",
                },
            }

            scenario = scenarios.get(scenario_type, scenarios["romantic_date"])

            # Получаем стилевой промпт для бота
            style_prompt = self._get_style_prompt(
                CommunicationStyle.ROMANTIC, user_gender, bot_gender
            )

            system_prompt = f"""
            Ты создаешь ролевой сценарий для флирта и романтического общения.
            
            СЦЕНАРИЙ: {scenario['title']}
            МЕСТО: {scenario['setting']}
            НАСТРОЕНИЕ: {scenario['mood']}
            АТМОСФЕРА: {scenario['atmosphere']}
            АКТИВНОСТИ: {', '.join(scenario['activities'])}
            
            ТВОЙ ПОЛ: {bot_gender.value}
            ПОЛ СОБЕСЕДНИКА: {user_gender.value}
            
            {style_prompt}
            
            ВАЖНЫЕ ПРАВИЛА ДЛЯ СЦЕНАРИЯ:
            1. ВСЕГДА помни пол собеседника ({user_gender.value}) и адаптируй стиль
            2. Создай краткое описание сценария (2-3 предложения) с учетом атмосферы
            3. Начни диалог в выбранном сценарии, используя один из стартеров: {scenario['dialogue_starters']}
            4. Будь игривым, романтичным и вовлекающим
            5. Поддерживай контекст сценария на протяжении всей беседы
            6. Используй детали окружения для создания атмосферы
            7. Не перескакивай с темы на тему без логической связи
            8. Создай ощущение реальности и присутствия в сценарии
            """

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": "Начни ролевую игру в этом сценарии"},
                ],
                max_tokens=400,
                temperature=0.9,
            )

            content = response.choices[0].message.content
            if content is not None and isinstance(content, str):
                return cast(Optional[str], content.strip())
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
