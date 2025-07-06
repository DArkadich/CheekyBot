#!/usr/bin/env python3
"""
Скрипт для оптимизации базы данных для масштабирования
"""
import asyncio
from datetime import datetime, timedelta

import asyncpg
from loguru import logger

from config.settings import settings


async def optimize_database() -> None:
    """Оптимизация базы данных для масштабирования"""

    # Подключение к базе данных
    conn = await asyncpg.connect(settings.database_url)

    try:
        logger.info("Начинаем оптимизацию базы данных...")

        # 1. Создание партиций для таблицы conversations
        await create_conversations_partitions(conn)

        # 2. Создание дополнительных индексов
        await create_optimized_indexes(conn)

        # 3. Создание материализованного представления для статистики
        await create_materialized_views(conn)

        # 4. Настройка автовакуума
        await configure_autovacuum(conn)

        # 5. Создание функции для очистки старых данных
        await create_cleanup_functions(conn)

        logger.info("Оптимизация базы данных завершена!")

    except Exception as e:
        logger.error(f"Ошибка при оптимизации: {e}")
        raise
    finally:
        await conn.close()


async def create_conversations_partitions(conn: asyncpg.Connection) -> None:
    """Создание партиций для таблицы conversations"""

    # Создаем партиции по месяцам
    current_date = datetime.now()

    for i in range(12):  # Создаем партиции на год вперед
        partition_date = current_date + timedelta(days=30 * i)
        partition_name = f"conversations_{partition_date.strftime('%Y_%m')}"

        # Создаем партицию
        await conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {partition_name} 
            PARTITION OF conversations 
            FOR VALUES FROM ('{partition_date.strftime('%Y-%m-01')}') 
            TO ('{(partition_date + timedelta(days=30)).strftime('%Y-%m-01')}')
        """
        )

        # Создаем индексы для партиции
        await conn.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{partition_name}_user_id 
            ON {partition_name} (user_id)
        """
        )

        await conn.execute(
            f"""
            CREATE INDEX IF NOT EXISTS idx_{partition_name}_created_at 
            ON {partition_name} (created_at)
        """
        )

    logger.info("Партиции для conversations созданы")


async def create_optimized_indexes(conn: asyncpg.Connection) -> None:
    """Создание оптимизированных индексов"""

    # Составной индекс для быстрого поиска по пользователю и дате
    await conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_conversations_user_date 
        ON conversations (user_id, created_at DESC)
    """
    )

    # Частичный индекс для активных пользователей
    await conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_users_active 
        ON users (user_id) WHERE is_active = true
    """
    )

    # Индекс для поиска по стилю общения
    await conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_conversations_style 
        ON conversations (communication_style, created_at DESC)
    """
    )

    logger.info("Оптимизированные индексы созданы")


async def create_materialized_views(conn: asyncpg.Connection) -> None:
    """Создание материализованных представлений"""

    # Представление для популярных стилей общения
    await conn.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS popular_styles AS
        SELECT 
            communication_style,
            COUNT(*) as usage_count,
            AVG(tokens_used) as avg_tokens
        FROM conversations 
        WHERE created_at >= NOW() - INTERVAL '30 days'
        GROUP BY communication_style
        ORDER BY usage_count DESC
    """
    )

    # Представление для активных пользователей
    await conn.execute(
        """
        CREATE MATERIALIZED VIEW IF NOT EXISTS active_users AS
        SELECT 
            u.user_id,
            u.first_name,
            COUNT(c.id) as message_count,
            MAX(c.created_at) as last_message
        FROM users u
        LEFT JOIN conversations c ON u.user_id = c.user_id
        WHERE u.is_active = true 
        AND c.created_at >= NOW() - INTERVAL '7 days'
        GROUP BY u.user_id, u.first_name
        ORDER BY message_count DESC
    """
    )

    logger.info("Материализованные представления созданы")


async def configure_autovacuum(conn: asyncpg.Connection) -> None:
    """Настройка автовакуума для оптимизации"""

    # Настройки автовакуума для таблицы conversations
    await conn.execute(
        """
        ALTER TABLE conversations SET (
            autovacuum_vacuum_scale_factor = 0.1,
            autovacuum_analyze_scale_factor = 0.05,
            autovacuum_vacuum_cost_limit = 2000
        )
    """
    )

    # Настройки для таблицы users
    await conn.execute(
        """
        ALTER TABLE users SET (
            autovacuum_vacuum_scale_factor = 0.2,
            autovacuum_analyze_scale_factor = 0.1
        )
    """
    )

    logger.info("Настройки автовакуума применены")


async def create_cleanup_functions(conn: asyncpg.Connection) -> None:
    """Создание функций для очистки старых данных"""

    # Функция для очистки старых диалогов
    await conn.execute(
        """
        CREATE OR REPLACE FUNCTION cleanup_old_conversations(days_to_keep INTEGER DEFAULT 90)
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            DELETE FROM conversations 
            WHERE created_at < NOW() - INTERVAL '1 day' * days_to_keep;
            
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            RETURN deleted_count;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Функция для архивирования неактивных пользователей
    await conn.execute(
        """
        CREATE OR REPLACE FUNCTION archive_inactive_users(days_inactive INTEGER DEFAULT 30)
        RETURNS INTEGER AS $$
        DECLARE
            archived_count INTEGER;
        BEGIN
            UPDATE users 
            SET is_active = false 
            WHERE user_id IN (
                SELECT u.user_id 
                FROM users u 
                LEFT JOIN conversations c ON u.user_id = c.user_id 
                WHERE c.created_at IS NULL 
                   OR c.created_at < NOW() - INTERVAL '1 day' * days_inactive
            );
            
            GET DIAGNOSTICS archived_count = ROW_COUNT;
            RETURN archived_count;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    logger.info("Функции очистки созданы")


async def create_scheduled_jobs() -> None:
    """Создание запланированных задач"""

    conn = await asyncpg.connect(settings.database_url)

    try:
        # Создаем расширение для планировщика
        await conn.execute("CREATE EXTENSION IF NOT EXISTS pg_cron")

        # Задача для обновления материализованных представлений
        await conn.execute(
            """
            SELECT cron.schedule(
                'update-popular-styles',
                '0 */6 * * *',  -- Каждые 6 часов
                'REFRESH MATERIALIZED VIEW popular_styles'
            );
        """
        )

        # Задача для очистки старых данных
        await conn.execute(
            """
            SELECT cron.schedule(
                'cleanup-old-data',
                '0 2 * * 0',  -- Каждое воскресенье в 2:00
                'SELECT cleanup_old_conversations(90)'
            );
        """
        )

        # Задача для архивирования неактивных пользователей
        await conn.execute(
            """
            SELECT cron.schedule(
                'archive-inactive-users',
                '0 3 * * 0',  -- Каждое воскресенье в 3:00
                'SELECT archive_inactive_users(30)'
            );
        """
        )

        logger.info("Запланированные задачи созданы")

    except Exception as e:
        logger.warning(f"Не удалось создать запланированные задачи: {e}")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(optimize_database())
    asyncio.run(create_scheduled_jobs())
