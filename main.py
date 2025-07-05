import asyncio
import sys
from loguru import logger
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode

from config.settings import settings
from database.connection import db
from handlers.user_handlers import router as user_router
from handlers.settings_handlers import router as settings_router
from handlers.roleplay_handlers import router as roleplay_router


async def main():
    """Главная функция запуска бота"""
    
    # Настройка логирования
    logger.remove()
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=settings.log_level
    )
    logger.add(
        "logs/bot.log",
        rotation="1 day",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=settings.log_level
    )
    
    logger.info("Starting CheekyBot...")
    
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.bot_token, parse_mode=ParseMode.HTML)
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
    async def error_handler(update, exception):
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