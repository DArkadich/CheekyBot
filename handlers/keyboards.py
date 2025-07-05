from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from database.models import CommunicationStyle, Gender


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💬 Начать общение")],
            [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="📊 Статистика")],
            [KeyboardButton(text="🎭 Ролевые игры"), KeyboardButton(text="❓ Помощь")],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие...",
    )
    return keyboard


def get_gender_selection_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора пола пользователя"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Мужской", callback_data="gender_male"),
                InlineKeyboardButton(text="👩 Женский", callback_data="gender_female"),
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Нейтральный", callback_data="gender_neutral"
                )
            ],
        ]
    )
    return keyboard


def get_bot_gender_selection_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора пола бота"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Парень", callback_data="bot_gender_male"),
                InlineKeyboardButton(
                    text="👩 Девушка", callback_data="bot_gender_female"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🤖 Нейтральный", callback_data="bot_gender_neutral"
                )
            ],
        ]
    )
    return keyboard


def get_communication_style_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора стиля общения"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="😊 Игривый", callback_data="style_playful"),
                InlineKeyboardButton(
                    text="💕 Романтичный", callback_data="style_romantic"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔥 Страстный", callback_data="style_passionate"
                ),
                InlineKeyboardButton(
                    text="🌙 Загадочный", callback_data="style_mysterious"
                ),
            ],
        ]
    )
    return keyboard


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Мой пол", callback_data="settings_gender")],
            [
                InlineKeyboardButton(
                    text="🤖 Пол бота", callback_data="settings_bot_gender"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 Стиль общения", callback_data="settings_style"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🚫 Стоп-слова", callback_data="settings_stop_words"
                )
            ],
            [InlineKeyboardButton(text="✅ Согласие", callback_data="settings_consent")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
        ]
    )
    return keyboard


def get_roleplay_scenarios_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора ролевых сценариев"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🍷 Романтическое свидание",
                    callback_data="scenario_romantic_date",
                ),
                InlineKeyboardButton(
                    text="🏖️ Пляжный роман", callback_data="scenario_beach_romance"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏔️ Горное приключение",
                    callback_data="scenario_mountain_adventure",
                ),
                InlineKeyboardButton(
                    text="🏙️ Исследование города",
                    callback_data="scenario_city_exploration",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏠 Уютный вечер дома", callback_data="scenario_cozy_home"
                )
            ],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")],
        ]
    )
    return keyboard


def get_consent_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура согласия на контент 18+"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Да, мне 18+", callback_data="consent_yes"),
                InlineKeyboardButton(text="❌ Нет", callback_data="consent_no"),
            ]
        ]
    )
    return keyboard


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой назад"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
        ]
    )
    return keyboard


def get_stop_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой остановки"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛑 Остановить", callback_data="stop_conversation"
                )
            ]
        ]
    )
    return keyboard
