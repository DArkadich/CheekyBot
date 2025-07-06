from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup
from loguru import logger

from database.connection import db
from database.models import Conversation, User
from handlers.keyboards import get_back_keyboard, get_stop_keyboard
from services.openai_service import openai_service

router = Router()


class RoleplayStates(StatesGroup):
    """Состояния для ролевых игр"""

    in_roleplay = State()


@router.callback_query(F.data.startswith("scenario_"))
async def start_roleplay_scenario(callback: CallbackQuery, state: FSMContext) -> None:
    """Начало ролевого сценария"""
    if callback.message is None:
        return
    user_id = callback.from_user.id
    user = await db.get_user(user_id)

    if user is None:
        await callback.message.edit_text(
            "❌ Сначала нужно зарегистрироваться! Используйте /start",
            reply_markup=get_back_keyboard(),
        )
        await callback.answer()
        return

    if not user.consent_given:
        await callback.message.edit_text(
            "⚠️ Для ролевых игр необходимо дать согласие на контент 18+",
            reply_markup=get_back_keyboard(),
        )
        await callback.answer()
        return

    scenario_type = callback.data.split("_", 1)[1]

    # Генерируем начало сценария
    scenario_start = await openai_service.generate_roleplay_scenario(
        scenario_type, user.gender, user.bot_gender
    )

    if scenario_start:
        await callback.message.edit_text(
            f"🎭 <b>Ролевая игра началась!</b>\n\n{scenario_start}\n\n"
            f"Продолжайте диалог, и я буду отвечать в стиле <b>{user.communication_style.value}</b>!",
            reply_markup=get_stop_keyboard(),
            parse_mode="HTML",
        )
        await state.set_state(RoleplayStates.in_roleplay)

        # Сохраняем начало сценария
        conversation = Conversation(
            id=0,
            user_id=user_id,
            message="Начало ролевой игры",
            bot_response=scenario_start,
            communication_style=user.communication_style,
            tokens_used=len(scenario_start.split()),
            created_at=datetime.now(),
        )
        await db.save_conversation(conversation)
    else:
        await callback.message.edit_text(
            "❌ Не удалось создать сценарий. Попробуйте еще раз.",
            reply_markup=get_back_keyboard(),
        )

    await callback.answer()


@router.message(RoleplayStates.in_roleplay)
async def handle_roleplay_message(message: Message, state: FSMContext) -> None:
    """Обработка сообщений в ролевой игре"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if user is None:
        await message.answer("Ошибка: пользователь не найден. Используйте /start")
        await state.clear()
        return

    if isinstance(message, Message) and message.text is None:
        await message.answer("Ошибка: пустое сообщение.")
        return

    # Проверяем стоп-слова
    if user.stop_words:
        if isinstance(message, Message) and message.text is not None:
            message_lower = message.text.lower()
            for word in user.stop_words:
                if word.lower() in message_lower:
                    await message.answer("Извини, но я не могу ответить на это сообщение.")
                    return

    # Генерируем ответ в контексте ролевой игры
    bot_response = await openai_service.generate_response(
        message.text,
        user.communication_style,
        user.gender,
        user.bot_gender,
        user.stop_words,
    )

    if bot_response:
        await message.answer(bot_response)

        # Сохраняем диалог в базу
        conversation = Conversation(
            id=0,
            user_id=user_id,
            message=message.text,
            bot_response=bot_response,
            communication_style=user.communication_style,
            tokens_used=len(message.text.split()) + len(bot_response.split()),
            created_at=datetime.now(),
        )
        await db.save_conversation(conversation)
    else:
        await message.answer("Извини, произошла ошибка. Попробуй еще раз.")


@router.callback_query(RoleplayStates.in_roleplay, F.data == "stop_conversation")
async def stop_roleplay(callback: CallbackQuery, state: FSMContext) -> None:
    """Остановка ролевой игры"""
    if callback.message is None:
        return
    await callback.message.edit_text(
        "🛑 Ролевая игра остановлена.\n\n"
        "Используйте '🎭 Ролевые игры' для начала нового сценария или "
        "'💬 Начать общение' для обычного общения.",
        reply_markup=get_back_keyboard(),
    )
    await state.clear()
    await callback.answer()
