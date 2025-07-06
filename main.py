import asyncio
import sys
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from loguru import logger

from config.settings import Settings, settings
from database.connection import db
from handlers.roleplay_handlers import router as roleplay_router
from handlers.settings_handlers import router as settings_router
from handlers.user_handlers import router as user_router


async def main() -> None:
    """Главная функция запуска бота"""

    # Используем settings или создаем новый экземпляр
    if settings is None:
        # В тестах или CI/CD создаем с дефолтными значениями
        app_settings = Settings(
            bot_token="dummy_token",
            openai_api_key="dummy_key",
            database_url="postgresql://test:test@localhost:5432/test_db",
            redis_url="redis://localhost:6379/0",
            openai_model="gpt-4-turbo-preview",
            log_level="INFO",
        )
    else:
        app_settings = settings

    # Настройка логирования
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=app_settings.log_level,
    )
    logger.add(
        "logs/bot.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=app_settings.log_level,
    )

    logger.info("Starting CheekyBot...")

    # Инициализация бота и диспетчера
    bot = Bot(token=app_settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Подключение к базе данных
    try:
        await db.connect()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        return

    # Регистрация роутеров
    dp.include_router(user_router)
    dp.include_router(settings_router)
    dp.include_router(roleplay_router)

    # Обработчик ошибок
    @dp.error()
    async def error_handler(update: Any, exception: Exception) -> bool:
        logger.error(f"Error handling update {update}: {exception}")
        return True

    logger.info("Bot started successfully!")

    try:
        # Запуск бота
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot stopped due to error: {e}")
    finally:
        # Закрытие соединений
        await db.close()
        await bot.session.close()
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
