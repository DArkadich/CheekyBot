import re
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from loguru import logger

from database.connection import db
from database.models import CommunicationStyle, Conversation, Gender, User
from handlers.keyboards import (
    get_back_keyboard,
    get_bot_gender_selection_keyboard,
    get_communication_style_keyboard,
    get_consent_keyboard,
    get_gender_selection_keyboard,
    get_main_menu_keyboard,
    get_roleplay_scenarios_keyboard,
    get_settings_keyboard,
    get_stop_keyboard,
)
from services.context_manager import context_manager
from services.openai_service import openai_service

router = Router()


class UserStates(StatesGroup):
    """Состояния пользователя для FSM"""

    waiting_for_gender = State()
    waiting_for_bot_gender = State()
    waiting_for_style = State()
    waiting_for_stop_words = State()
    waiting_for_consent = State()
    in_conversation = State()


@router.message(Command("start"))  # type: ignore[misc]
async def cmd_start(message: Message, state: FSMContext) -> None:
    """Обработчик команды /start"""
    user_id = message.from_user.id

    # Проверяем, существует ли пользователь
    user = await db.get_user(user_id)

    if user is not None:
        # Пользователь уже существует
        await message.answer(
            f"Привет, {user.first_name}! 👋\nРад снова тебя видеть!",
            reply_markup=get_main_menu_keyboard(),
        )
        await state.clear()
    else:
        # Новый пользователь - начинаем регистрацию
        await message.answer(
            "Привет! 👋 Я бот для флирта и романтического общения.\n\n"
            "Для начала давай познакомимся! Какой у тебя пол?",
            reply_markup=get_gender_selection_keyboard(),
        )
        await state.set_state(UserStates.waiting_for_gender)


@router.message(Command("help"))  # type: ignore[misc]
async def cmd_help(message: Message) -> None:
    """Обработчик команды /help"""
    help_text = """
🤖 <b>CheekyBot - Бот для флирта и романтического общения</b>

<b>Основные команды:</b>
/start - Начать общение
/help - Показать эту справку
/settings - Настройки профиля
/stats - Ваша статистика

<b>Возможности:</b>
• 4 стиля общения: игривый, романтичный, страстный, загадочный
• Настройка пола бота (М/Ж/Нейтральный)
• Ролевые сценарии
• Система стоп-слов для безопасности
• Адаптивное общение с ИИ

<b>Безопасность:</b>
• Всегда уважаем ваши границы
• Можно остановить общение в любой момент
• Система согласия на контент 18+

<b>Начните с команды /start для регистрации!</b>
    """
    await message.answer(help_text, parse_mode="HTML")


@router.message(Command("settings"))  # type: ignore[misc]
async def cmd_settings(message: Message) -> None:
    """Обработчик команды /settings"""
    await message.answer(
        "⚙️ <b>Настройки профиля</b>\n\nВыберите, что хотите изменить:",
        reply_markup=get_settings_keyboard(),
        parse_mode="HTML",
    )


@router.message(Command("stats"))  # type: ignore[misc]
async def cmd_stats(message: Message) -> None:
    """Обработчик команды /stats"""
    user_id = message.from_user.id
    stats = await db.get_user_stats(user_id)

    if stats is not None:
        stats_text = f"""
📊 <b>Ваша статистика</b>

💬 Сообщений: {stats.total_messages}
🔤 Токенов использовано: {stats.total_tokens}
❤️ Любимый стиль: {stats.favorite_style.value}
🕐 Последняя активность: {stats.last_activity.strftime('%d.%m.%Y %H:%M')}
        """
    else:
        stats_text = "📊 Статистика пока недоступна. Начните общение!"

    await message.answer(stats_text, parse_mode="HTML")


@router.message(F.text == "💬 Начать общение")  # type: ignore[misc]
async def start_conversation(message: Message, state: FSMContext) -> None:
    """Начало общения с ботом"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if user is None:
        await message.answer("Сначала нужно зарегистрироваться! Используйте /start")
        return

    if not user.consent_given:
        await message.answer(
            "⚠️ Для начала общения необходимо дать согласие на контент 18+",
            reply_markup=get_consent_keyboard(),
        )
        await state.set_state(UserStates.waiting_for_consent)
        return

    await message.answer(
        f"Отлично! Начинаем общение в стиле <b>{user.communication_style.value}</b> 😊\n\n"
        "Просто напишите мне что-нибудь, и я отвечу!",
        reply_markup=get_stop_keyboard(),
        parse_mode="HTML",
    )
    await state.set_state(UserStates.in_conversation)


@router.message(F.text == "⚙️ Настройки")  # type: ignore[misc]
async def show_settings(message: Message) -> None:
    """Показать настройки"""
    await cmd_settings(message)


@router.message(F.text == "📊 Статистика")  # type: ignore[misc]
async def show_stats(message: Message) -> None:
    """Показать статистику"""
    await cmd_stats(message)


@router.message(F.text == "🎭 Ролевые игры")  # type: ignore[misc]
async def show_roleplay(message: Message) -> None:
    """Показать ролевые сценарии"""
    await message.answer(
        "🎭 <b>Ролевые сценарии</b>\n\nВыберите интересующий вас сценарий:",
        reply_markup=get_roleplay_scenarios_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text == "❓ Помощь")  # type: ignore[misc]
async def show_help(message: Message) -> None:
    """Показать помощь"""
    await cmd_help(message)


def contains_profanity(text: str) -> bool:
    profanities = [
        "хуй",
        "бляд",
        "пизд",
        "еба",
        "нахуй",
        "сука",
        "наебн",
        "мудил",
        "гандон",
    ]
    return any(re.search(rf"\b{word}", text, re.IGNORECASE) for word in profanities)


def detect_poetic_mood(text: str) -> tuple[bool, str]:
    """Анализирует текст пользователя и определяет, нужен ли поэтический режим и настроение."""
    poetic_triggers = [
        (
            "alcohol",
            [
                "налей",
                "коньяк",
                "виски",
                "бар",
                "собутыльник",
                "бухать",
                "выпить",
                "рюмка",
                "перетереть",
                "за жизнь",
            ],
        ),
        (
            "boredom",
            [
                "скучно",
                "развесели",
                "развлеки",
                "игра",
                "играть",
                "шутка",
                "пошути",
                "анекдот",
            ],
        ),
        (
            "sad",
            [
                "грусть",
                "тоска",
                "одиночество",
                "печаль",
                "устал",
                "устала",
                "грустно",
                "одинок",
                "одиноко",
            ],
        ),
        (
            "poetry",
            [
                "стих",
                "рифма",
                "поэма",
                "в рифму",
                "поэтически",
                "поэзию",
                "стихотворение",
            ],
        ),
    ]
    text_lower = text.lower()
    for mood, keywords in poetic_triggers:
        if any(word in text_lower for word in keywords):
            return True, mood
    return False, ""


@router.message(UserStates.in_conversation)  # type: ignore[misc]
async def handle_conversation(message: Message, state: FSMContext) -> None:
    """Обработка сообщений в режиме общения с оптимизированным контекстом"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)

    if user is None:
        await message.answer("Ошибка: пользователь не найден. Используйте /start")
        await state.clear()
        return

    if isinstance(message, Message) and message.text is not None:
        # Проверяем стоп-слова
        if user.stop_words:
            message_lower = message.text.lower()
            for word in user.stop_words:
                if word.lower() in message_lower:
                    await message.answer(
                        "Извини, но я не могу ответить на это сообщение."
                    )
                    return

        # Получаем оптимизированный контекст
        conversation_history = await context_manager.get_optimized_context(
            user_id, max_tokens=800
        )

        # Определяем, использовал ли пользователь мат в последних 5 сообщениях
        recent_history = await db.get_recent_conversations(user_id, limit=5)
        user_used_profanity = any(
            contains_profanity(conv.message) for conv in recent_history
        )

        # Анализируем настроение пользователя
        poetic, mood = detect_poetic_mood(message.text)

        # Формируем prompt через openai_service
        bot_response = await openai_service.generate_response(
            message.text,
            user.communication_style,
            user.gender,
            user.bot_gender,
            conversation_history,
            user.stop_words,
            poetic=poetic,
            mood=mood,
        )

        if bot_response:
            await message.answer(bot_response)
            await context_manager.add_message_to_context(
                user_id, message.text, bot_response, user.communication_style.value
            )
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
    else:
        await message.answer("Ошибка: пустое сообщение.")


# Обработчики callback-запросов
@router.callback_query(F.data.startswith("gender_"))  # type: ignore[misc]
async def handle_gender_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка выбора пола пользователя"""
    if callback.message is None:
        return
    gender_value = callback.data.split("_")[1]
    gender = Gender(gender_value)

    await state.update_data(user_gender=gender)

    await callback.message.edit_text(
        f"Отлично! Теперь выбери пол бота:",
        reply_markup=get_bot_gender_selection_keyboard(),
    )
    await state.set_state(UserStates.waiting_for_bot_gender)
    await callback.answer()


@router.callback_query(F.data.startswith("bot_gender_"))  # type: ignore[misc]
async def handle_bot_gender_selection(
    callback: CallbackQuery, state: FSMContext
) -> None:
    """Обработка выбора пола бота"""
    if callback.message is None:
        return
    bot_gender_value = callback.data.split("_")[2]
    bot_gender = Gender(bot_gender_value)

    await state.update_data(bot_gender=bot_gender)

    await callback.message.edit_text(
        f"Отлично! Теперь выбери стиль общения:",
        reply_markup=get_communication_style_keyboard(),
    )
    await state.set_state(UserStates.waiting_for_style)
    await callback.answer()


@router.callback_query(F.data.startswith("style_"))  # type: ignore[misc]
async def handle_style_selection(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка выбора стиля общения"""
    if callback.message is None:
        return
    style_value = callback.data.split("_")[1]
    style = CommunicationStyle(style_value)

    data = await state.get_data()
    user_gender = data.get("user_gender")
    bot_gender = data.get("bot_gender")

    if user_gender is None or bot_gender is None:
        await callback.message.edit_text("Ошибка: не выбран пол пользователя или бота.")
        await callback.answer()
        return

    user_id = callback.from_user.id
    existing_user = await db.get_user(user_id)
    if existing_user is not None:
        await callback.message.edit_text(
            "Пользователь уже зарегистрирован. Используйте /settings для изменения профиля.",
            reply_markup=get_settings_keyboard(),
        )
        await state.clear()
        await callback.answer()
        return

    # Создаем пользователя
    user = User(
        user_id=user_id,
        username=callback.from_user.username,
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name,
        gender=user_gender,
        bot_gender=bot_gender,
        communication_style=style,
        consent_given=False,
        stop_words=[],
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    await db.create_user(user)

    await callback.message.edit_text(
        f"Отлично! Регистрация завершена! 🎉\n\n"
        f"Твой пол: {user_gender.value}\n"
        f"Пол бота: {bot_gender.value}\n"
        f"Стиль общения: {style.value}\n\n"
        f"Теперь нужно дать согласие на контент 18+:",
        reply_markup=get_consent_keyboard(),
    )
    await state.set_state(UserStates.waiting_for_consent)
    await callback.answer()


@router.callback_query(F.data == "consent_yes")  # type: ignore[misc]
async def handle_consent_yes(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка согласия на контент 18+"""
    user_id = callback.from_user.id
    user = await db.get_user(user_id)

    if user:
        user.consent_given = True
        await db.update_user(user)

    await callback.message.edit_text(
        "✅ Согласие получено! Теперь можно начинать общение.\n\n"
        "Используйте кнопку '💬 Начать общение' для старта!",
        reply_markup=get_back_keyboard(),
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "consent_no")  # type: ignore[misc]
async def handle_consent_no(callback: CallbackQuery, state: FSMContext) -> None:
    """Обработка отказа от контента 18+"""
    await callback.message.edit_text(
        "❌ Без согласия на контент 18+ бот не может работать.\n\n"
        "Если передумаете, используйте /start для повторной регистрации.",
        reply_markup=get_back_keyboard(),
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "back_to_main")  # type: ignore[misc]
async def handle_back_to_main(callback: CallbackQuery, state: FSMContext) -> None:
    """Возврат в главное меню"""
    await callback.message.edit_text("Главное меню:", reply_markup=get_back_keyboard())
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "stop_conversation")  # type: ignore[misc]
async def handle_stop_conversation(callback: CallbackQuery, state: FSMContext) -> None:
    """Остановка общения"""
    await callback.message.edit_text(
        "🛑 Общение остановлено.\n\nИспользуйте '💬 Начать общение' для возобновления.",
        reply_markup=get_back_keyboard(),
    )
    await state.clear()
    await callback.answer()


@router.message(Command("clear_context"))  # type: ignore[misc]
async def cmd_clear_context(message: Message) -> None:
    """Очистка контекста диалога"""
    user_id = message.from_user.id

    await context_manager.clear_context(user_id)

    await message.answer(
        "🧹 Контекст диалога очищен! Теперь я буду отвечать как при первом знакомстве."
    )


@router.message(Command("context_info"))  # type: ignore[misc]
async def cmd_context_info(message: Message) -> None:
    """Информация о текущем контексте"""
    user_id = message.from_user.id

    context = await context_manager.get_context(user_id)
    preferences = await context_manager.get_user_preferences(user_id)

    context_info = f"""
📊 <b>Информация о контексте</b>

💬 Сообщений в контексте: {len(context) // 2}
🎭 Предпочитаемый стиль: {preferences['communication_style']}
😊 Настроение: {preferences['mood']}
📝 Темы: {', '.join(preferences['topics']) if preferences['topics'] else 'не определены'}

<i>Контекст автоматически очищается через час неактивности</i>
    """

    await message.answer(context_info, parse_mode="HTML")


@router.message(Command("persona"))  # type: ignore[misc]
async def cmd_persona(message: Message, state: FSMContext) -> None:
    """Смена личности пользователя (default/poet)"""
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    if user is None:
        await message.answer("Сначала зарегистрируйтесь через /start.")
        return
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Укажите личность: /persona poet или /persona default")
        return
    persona = args[1].strip().lower()
    if persona not in ("default", "poet"):
        await message.answer("Доступные личности: default, poet")
        return
    user.persona = persona
    await db.update_user(user)
    await message.answer(f"Личность бота теперь: {persona}")
