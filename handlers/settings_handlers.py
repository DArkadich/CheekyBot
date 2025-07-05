from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from database.connection import db
from database.models import CommunicationStyle, Gender, User
from handlers.keyboards import (
    get_back_keyboard,
    get_bot_gender_selection_keyboard,
    get_communication_style_keyboard,
    get_gender_selection_keyboard,
    get_settings_keyboard,
)

router = Router()


class SettingsStates(StatesGroup):
    """Состояния для настроек"""

    waiting_for_gender = State()
    waiting_for_bot_gender = State()
    waiting_for_style = State()
    waiting_for_stop_words = State()


@router.callback_query(F.data == "settings_gender")
async def settings_gender(callback: CallbackQuery, state: FSMContext):
    """Настройка пола пользователя"""
    await callback.message.edit_text(
        "👤 <b>Выберите ваш пол:</b>",
        reply_markup=get_gender_selection_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(SettingsStates.waiting_for_gender)
    await callback.answer()


@router.callback_query(F.data == "settings_bot_gender")
async def settings_bot_gender(callback: CallbackQuery, state: FSMContext):
    """Настройка пола бота"""
    await callback.message.edit_text(
        "🤖 <b>Выберите пол бота:</b>",
        reply_markup=get_bot_gender_selection_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(SettingsStates.waiting_for_bot_gender)
    await callback.answer()


@router.callback_query(F.data == "settings_style")
async def settings_style(callback: CallbackQuery, state: FSMContext):
    """Настройка стиля общения"""
    await callback.message.edit_text(
        "💬 <b>Выберите стиль общения:</b>",
        reply_markup=get_communication_style_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(SettingsStates.waiting_for_style)
    await callback.answer()


@router.callback_query(F.data == "settings_stop_words")
async def settings_stop_words(callback: CallbackQuery, state: FSMContext):
    """Настройка стоп-слов"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)

    if user and user.stop_words:
        current_words = ", ".join(user.stop_words)
        text = f"🚫 <b>Текущие стоп-слова:</b>\n{current_words}\n\nОтправьте новые стоп-слова через запятую или 'нет' для очистки:"
    else:
        text = "🚫 <b>Стоп-слова не установлены</b>\n\nОтправьте стоп-слова через запятую или 'нет' для пропуска:"

    await callback.message.edit_text(text, parse_mode="HTML")
    await state.set_state(SettingsStates.waiting_for_stop_words)
    await callback.answer()


@router.callback_query(F.data == "settings_consent")
async def settings_consent(callback: CallbackQuery):
    """Настройка согласия"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)

    if user and user.consent_given:
        text = "✅ <b>Согласие на контент 18+ уже дано</b>\n\nЕсли хотите отозвать согласие, используйте /start для повторной регистрации."
    else:
        text = "❌ <b>Согласие на контент 18+ не дано</b>\n\nДля работы бота необходимо дать согласие."

    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=get_back_keyboard()
    )
    await callback.answer()


# Обработчики изменения настроек
@router.callback_query(SettingsStates.waiting_for_gender, F.data.startswith("gender_"))
async def change_gender(callback: CallbackQuery, state: FSMContext):
    """Изменение пола пользователя"""
    gender_value = callback.data.split("_")[1]
    gender = Gender(gender_value)

    user_id = callback.from_user.id
    user = await db.get_user(user_id)

    if user:
        user.gender = gender
        await db.update_user(user)

        await callback.message.edit_text(
            f"✅ <b>Пол успешно изменен на: {gender.value}</b>",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка: пользователь не найден", reply_markup=get_back_keyboard()
        )

    await state.clear()
    await callback.answer()


@router.callback_query(
    SettingsStates.waiting_for_bot_gender, F.data.startswith("bot_gender_")
)
async def change_bot_gender(callback: CallbackQuery, state: FSMContext) -> None:
    """Изменение пола бота"""
    bot_gender_value = callback.data.split("_")[2]
    bot_gender = Gender(bot_gender_value)

    user_id = callback.from_user.id
    user = await db.get_user(user_id)

    if user:
        user.bot_gender = bot_gender
        await db.update_user(user)

        await callback.message.edit_text(
            f"✅ <b>Пол бота успешно изменен на: {bot_gender.value}</b>",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка: пользователь не найден", reply_markup=get_back_keyboard()
        )

    await state.clear()
    await callback.answer()


@router.callback_query(SettingsStates.waiting_for_style, F.data.startswith("style_"))
async def change_style(callback: CallbackQuery, state: FSMContext) -> None:
    """Изменение стиля общения"""
    style_value = callback.data.split("_")[1]
    style = CommunicationStyle(style_value)

    user_id = callback.from_user.id
    user = await db.get_user(user_id)

    if user:
        user.communication_style = style
        await db.update_user(user)

        await callback.message.edit_text(
            f"✅ <b>Стиль общения успешно изменен на: {style.value}</b>",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(
            "❌ Ошибка: пользователь не найден", reply_markup=get_back_keyboard()
        )

    await state.clear()
    await callback.answer()


@router.message(SettingsStates.waiting_for_stop_words)
async def change_stop_words(message: Message, state: FSMContext) -> None:
    """Изменение стоп-слов"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if not user:
        await message.answer("❌ Ошибка: пользователь не найден")
        await state.clear()
        return

    text = message.text.strip().lower()

    if text == "нет":
        user.stop_words = []
        await db.update_user(user)
        await message.answer(
            "✅ <b>Стоп-слова очищены</b>",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML",
        )
    else:
        # Разбираем стоп-слова
        stop_words = [word.strip() for word in text.split(",") if word.strip()]
        user.stop_words = stop_words
        await db.update_user(user)

        words_text = ", ".join(stop_words)
        await message.answer(
            f"✅ <b>Стоп-слова установлены:</b>\n{words_text}",
            reply_markup=get_back_keyboard(),
            parse_mode="HTML",
        )

    await state.clear()
