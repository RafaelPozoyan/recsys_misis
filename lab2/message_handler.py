"""
Обработка сообщений бота - выбор модели и жанра
/start -> выбор модели -> выбор жанра -> генерация ответа.
"""

from typing import Dict, List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from gpt_model import GPTModel
from llama_model import LLaMAModel
from app_types import GENRE_DESCRIPTIONS, ModelType, MovieGenre


class MessageHandler:
    """
    Управляет состоянием выбора пользователя и выдачей рекомендаций

    Args:
        Update и Context.
    """

    def __init__(self) -> None:
        """
        Инициализирует 2 модели и хранилище выбора пользователя
        """
        self.gpt_model: GPTModel = GPTModel()
        self.llama_model: LLaMAModel = LLaMAModel()
        self.user_choices: Dict[int, Dict[str, str]] = {}

    async def start_command_handler(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Бот начинает работу и предлагает выбор моделей

        Args:
            update: Update
            context: ContextTypes.DEFAULT_TYPE
        """
        keyboard: List[List[InlineKeyboardButton]] = [
            [InlineKeyboardButton("GPT (Llama-3.1) (HF)", callback_data="model_gpt")],
            [
                InlineKeyboardButton(
                    "LLaMA-3.1-8B Instruct (HF)", callback_data="model_llama"
                )
            ],
        ]
        reply_markup: InlineKeyboardMarkup = InlineKeyboardMarkup(keyboard)

        text: str = (
            "Привет. Это бот, рекомендующий фильмы .\n\n"
            "Сначала выбери модель:\n"
            "1) GPT-класс: Llama-3.1-8B-Instruct (через Router API)\n"
            "2) LLaMA-класс: Llama-3.1-8B-Instruct"
        )
        await update.message.reply_text(text, reply_markup=reply_markup)

    async def handle_model_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Сохраняет выбранную модель и предлагает выбрать жанр

        Args:
            update: Update
            context: ContextTypes.DEFAULT_TYPE
        """
        query = update.callback_query
        await query.answer()

        user_id: int = update.effective_user.id
        data: str = query.data

        selected_model: str = ModelType.GPT if data == "model_gpt" else ModelType.LLAMA
        self.user_choices.setdefault(user_id, {})["model"] = selected_model

        genres: List[MovieGenre] = list(MovieGenre)
        keyboard: List[List[InlineKeyboardButton]] = [
            [InlineKeyboardButton(g.value, callback_data=f"genre_{g.name.lower()}")]
            for g in genres
        ]

        await query.edit_message_text(
            text="Модель выбрана. Теперь выбери жанр:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def handle_genre_selection(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE
    ) -> None:
        """
        Сохраняет жанр, формирую промпт и вызывает выбранную модель

        Args:
            update: Update
            context: ContextTypes.DEFAULT_TYPE
        """
        query = update.callback_query
        await query.answer()

        user_id: int = update.effective_user.id
        data: str = query.data

        genre_name: str = data.replace("genre_", "").upper()
        selected_genre: MovieGenre = MovieGenre[genre_name]

        self.user_choices.setdefault(user_id, {})["genre"] = selected_genre.value
        selected_model: str = self.user_choices[user_id].get("model", ModelType.GPT)

        await query.edit_message_text(
            "Генерирую рекомендацию через Hugging Face Inference API..."
        )

        genre_desc: str = GENRE_DESCRIPTIONS[selected_genre]
        user_prompt: str = (
            f"Порекомендуй один {genre_desc}.\n"
            "Укажи название (год), актеров, кратко опиши сюжет (2-3 предложения) и почему стоит смотреть."
        )

        try:
            if selected_model == ModelType.GPT:
                response: str = await self.gpt_model.generate_response(user_prompt)
                prefix: str = "Ответ GPT:"
            else:
                response: str = await self.llama_model.generate_response(user_prompt)
                prefix: str = "Ответ LLaMA-3.1:"

            await query.edit_message_text(f"{prefix}\n\n{response}")

        except Exception as e:
            await query.edit_message_text(f"❌ Ошибка генерации: {e}")
