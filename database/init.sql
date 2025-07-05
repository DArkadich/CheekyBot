-- Инициализация базы данных CheekyBot

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создание таблиц
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    gender VARCHAR(20) NOT NULL DEFAULT 'neutral',
    bot_gender VARCHAR(20) NOT NULL DEFAULT 'neutral',
    communication_style VARCHAR(20) NOT NULL DEFAULT 'playful',
    consent_given BOOLEAN NOT NULL DEFAULT FALSE,
    stop_words TEXT[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    communication_style VARCHAR(20) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_stats (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    total_messages INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    favorite_style VARCHAR(20) DEFAULT 'playful',
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Создание индексов для производительности
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_consent_given ON users(consent_given);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);

-- Создание триггеров для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_stats_updated_at BEFORE UPDATE ON user_stats
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Создание представления для статистики
CREATE OR REPLACE VIEW user_statistics AS
SELECT 
    u.user_id,
    u.username,
    u.first_name,
    u.communication_style,
    us.total_messages,
    us.total_tokens,
    us.favorite_style,
    us.last_activity,
    u.created_at as registration_date
FROM users u
LEFT JOIN user_stats us ON u.user_id = us.user_id
WHERE u.is_active = TRUE;

-- Создание пользователя для приложения (если не существует)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_user WHERE usename = 'cheekybot') THEN
        CREATE USER cheekybot WITH PASSWORD 'password';
    END IF;
END
$$;

-- Предоставление прав пользователю
GRANT ALL PRIVILEGES ON DATABASE cheekybot TO cheekybot;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cheekybot;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cheekybot;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO cheekybot;

-- Установка прав по умолчанию для новых таблиц
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cheekybot;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO cheekybot;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO cheekybot; 