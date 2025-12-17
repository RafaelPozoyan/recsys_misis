"""
Обработка сообщений Telegram-бота (выбор модели и жанра).

Что я делаю?
    Веду диалог: /start -> выбор модели -> выбор жанра -> генерация ответа.

Что я принимаю на вход?
    Update, Context (telegram.ext)

Что я возвращаю?
    None (отправляю сообщения пользователю).
"""

from typing import Dict, List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from gpt_model import GPTModel
from llama_model import LLaMAModel
from app_types import GENRE_DESCRIPTIONS, ModelType, MovieGenre


class MessageHandler:
    """
    Что я делаю?
        Управляю состоянием выбора пользователя и выдачей рекомендаций.

    Что я принимаю на вход?
        Update и Context.

    Что я возвращаю?
        None (сообщения отправляются в Telegram).
    """

    def __init__(self) -> None:
        """
        Что я делаю?
            Инициализирую 2 модели и хранилище выбора пользователя.

        Что я принимаю на вход?
            Ничего.

        Что я возвращаю?
            None
        """
        self.gpt_model: GPTModel = GPTModel()
        self.llama_model: LLaMAModel = LLaMAModel()
        self.user_choices: Dict[int, Dict[str, str]] = {}

    async def start_command_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Что я делаю?
            Приветствую и предлагаю выбрать модель.

        Что я принимаю на вход?
            update: Update
            context: ContextTypes.DEFAULT_TYPE

        Что я возвращаю?
            None
        """
        keyboard: List[List[InlineKeyboardButton]] = [
            [InlineKeyboardButton("🧠 ruGPT-3 (HF)", callback_data="model_gpt")],
            [InlineKeyboardButton("🦙 LLaMA-2-7B Chat (HF)", callback_data="model_llama")],
        ]
        reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(keyboard)

        text: str = (
            "🎬 Привет! Это бот-рекомендатель фильмов.\n\n"
            "Сначала выбери модель (по методичке):\n"
            "1) GPT-класс: ruGPT3medium_based_on_gpt2\n"
            "2) LLaMA-класс: Llama-2-7b-chat-hf"
        )
        await update.message.reply_text(text, reply_markup=reply_markup)

    async def handle_model_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Что я делаю?
            Сохраняю выбранную модель и предлагаю выбрать жанр.

        Что я принимаю на вход?
            update: Update
            context: ContextTypes.DEFAULT_TYPE

        Что я возвращаю?
            None
        """
        query = update.callback_query
        await query.answer()

        user_id: int = update.effective_user.id
        data: str = query.data

        selected_model: str = ModelType.GPT if data == "model_gpt" else ModelType.LLAMA
        self.user_choices.setdefault(user_id, {})["model"] = selected_model

        genres: List[MovieGenre] = list(MovieGenre)
        keyboard: List[List[InlineKeyboardButton]] = [
            [InlineKeyboardButton(g.value, callback_data=f"genre_{g.name.lower()}")] for g in genres
        ]

        await query.edit_message_text(
            text="✅ Модель выбрана. Теперь выбери жанр кино:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def handle_genre_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Что я делаю?
            Сохраняю жанр, формирую промпт и вызываю выбранную HF-модель асинхронно.

        Что я принимаю на вход?
            update: Update
            context: ContextTypes.DEFAULT_TYPE

        Что я возвращаю?
            None
        """
        query = update.callback_query
        await query.answer()

        user_id: int = update.effective_user.id
        data: str = query.data

        genre_name: str = data.replace("genre_", "").upper()
        selected_genre: MovieGenre = MovieGenre[genre_name]

        self.user_choices.setdefault(user_id, {})["genre"] = selected_genre.value
        selected_model: str = self.user_choices[user_id].get("model", ModelType.GPT)

        await query.edit_message_text("⏳ Генерирую рекомендацию через Hugging Face Inference API...")

        genre_desc: str = GENRE_DESCRIPTIONS[selected_genre]
        user_prompt: str = (
            f"Порекомендуй один {genre_desc}.\n"
            "Укажи название (год), актеров, краткий сюжет (2-3 предложения) и почему стоит смотреть."
        )

        try:
            if selected_model == ModelType.GPT:
                response: str = await self.gpt_model.generate_response(user_prompt)
                prefix: str = "🧠 Ответ ruGPT-3 (HF):"
            else:
                response: str = await self.llama_model.generate_response(user_prompt)
                prefix: str = "🦙 Ответ LLaMA-2 (HF):"

            await query.edit_message_text(f"{prefix}\n\n{response}")

        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка генерации: {e}")

    async def help_command_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Что я делаю?
            Показываю справку по боту.

        Что я принимаю на вход?
            update: Update
            context: ContextTypes.DEFAULT_TYPE

        Что я возвращаю?
            None
        """
        await update.message.reply_text(
            "Команды:\n"
            "/start — начать\n"
            "/help — справка\n\n"
            "Алгоритм: /start → выбрать модель → выбрать жанр → получить рекомендацию."
        )
