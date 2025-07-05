from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


class CommunicationStyle(str, Enum):
    PLAYFUL = "playful"
    ROMANTIC = "romantic"
    PASSIONATE = "passionate"
    MYSTERIOUS = "mysterious"


@dataclass
class User:
    user_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    gender: Gender
    bot_gender: Gender
    communication_style: CommunicationStyle
    consent_given: bool
    stop_words: List[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True


@dataclass
class Conversation:
    id: int
    user_id: int
    message: str
    bot_response: str
    communication_style: CommunicationStyle
    tokens_used: int
    created_at: datetime


@dataclass
class UserStats:
    user_id: int
    total_messages: int
    total_tokens: int
    favorite_style: CommunicationStyle
    last_activity: datetime
    created_at: datetime
    updated_at: datetime


# SQL queries for database operations
CREATE_TABLES_SQL = """
-- Users table
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

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(user_id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    bot_response TEXT NOT NULL,
    communication_style VARCHAR(20) NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User statistics table
CREATE TABLE IF NOT EXISTS user_stats (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    total_messages INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    favorite_style VARCHAR(20) DEFAULT 'playful',
    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
"""
