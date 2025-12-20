from __future__ import annotations

import json
import os
from typing import Dict, List

from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from cf_user_cosine import Recommendation, UserBasedCosineCF
from storage_json import RatingTriplet, load_ratings, save_ratings, upsert_rating


def main_keyboard() -> ReplyKeyboardMarkup:
    """
    Создает клавиатуру с кнопками-командами

    Returns:
        ReplyKeyboardMarkup: Объект клавиатуры Telegram
    """
    keyboard: List[List[KeyboardButton]] = [
        [KeyboardButton("/recommend")],
        [KeyboardButton("/start")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)


def load_movie_titles(movies_file_path: str) -> Dict[int, str]:
    """
    Загружает отображение movie_id -> movie_title из файла movies.json

    Args:
        movies_file_path: Путь к файлу movies.json

    Returns:
        Dict[int, str]: Словарь {movie_id(int): title(str)}
    """
    with open(movies_file_path, "r", encoding="utf-8") as file:
        raw: Dict[str, str] = json.load(file)

    return {int(movie_id): title for movie_id, title in raw.items()}


def get_movie_titles(context: ContextTypes.DEFAULT_TYPE) -> Dict[int, str]:
    """
    Достает словарь movie_id -> title из application.bot_data.

    Args:
        context: Контекст обработчика Telegram (для доступа к context.application.bot_data).

    Returns:
        Dict[int, str]: Словарь {movie_id: title}. Если данных нет или тип неверный, возвращает пустой словарь.
    """
    movie_titles_obj: object = context.application.bot_data.get("movie_titles", {})
    if isinstance(movie_titles_obj, dict):
        return movie_titles_obj
    return {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляет приветственное сообщение и показывает команды бота.

    Args:
        update: Объект Telegram Update (содержит входящее сообщение и данные пользователя).
        context: Контекст обработчика Telegram.

    Returns:
        None.
    """
    if update.message is None:
        return

    await update.message.reply_text(
        "Привет. Я — бот, рекомендующий фильмы по косинусному сходству (User-Based CF).\n\n"
        "Команды:\n"
        "/rate <id фильма> <рейтинг> — рейтинг от 1 до 5\n"
        "/recommend — рекомендации\n",
        reply_markup=main_keyboard(),
    )


async def rate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Принимает оценку фильма от пользователя и сохраняет/обновляет её в ratings.json.

    Команда:
        /rate <id фильма> <rating>

    Args:
        update: Объект Telegram Update.
        context: Контекст обработчика Telegram (в context.args лежат аргументы команды).

    Returns:
        None.
    """
    if update.message is None:
        return

    args: List[str] = list(context.args)
    if len(args) != 2:
        await update.message.reply_text(
            "Необходимый формат: /rate <id фильма> <rating>",
            reply_markup=main_keyboard(),
        )
        return

    try:
        item_id: int = int(args[0])
        rating_value: float = float(args[1])
    except ValueError:
        await update.message.reply_text(
            "Ошибка: id и рейтинг фильма должны быть типа int",
            reply_markup=main_keyboard(),
        )
        return

    if not (1.0 <= rating_value <= 5.0):
        await update.message.reply_text(
            "Ошибка: rating должен быть в диапазоне от 1 до 5.",
            reply_markup=main_keyboard(),
        )
        return

    user_id: int = int(update.effective_user.id)
    ratings_file_path: str = "ratings.json"
    movie_titles: Dict[int, str] = get_movie_titles(context)

    current_ratings: List[RatingTriplet] = load_ratings(ratings_file_path)
    updated_ratings: List[RatingTriplet] = upsert_rating(
        ratings=current_ratings,
        user_id=user_id,
        item_id=item_id,
        rating=rating_value,
    )
    save_ratings(ratings_file_path, updated_ratings)

    await update.message.reply_text(
        f"Сохранено:\n{movie_titles.get(item_id)}\n"
        f"id = {item_id} | рейтинг = {rating_value:.1f}",
        reply_markup=main_keyboard(),
    )


async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Строит рекомендации по User-Based Collaborative Filtering с косинусным сходством
    и отправляет пользователю список рекомендованных фильмов с названиями.

    Args:
        update: Объект Telegram Update.
        context: Контекст обработчика Telegram.

    Returns:
        None.
    """
    if update.message is None:
        return

    user_id: int = int(update.effective_user.id)
    ratings_file_path: str = "ratings.json"
    movie_titles: Dict[int, str] = get_movie_titles(context)

    all_ratings: List[RatingTriplet] = load_ratings(ratings_file_path)

    model: UserBasedCosineCF = UserBasedCosineCF(ratings=all_ratings)
    recommendations: List[Recommendation] = model.recommend_items(
        target_user_id=user_id,
        neighbors_k=10,
        recommendations_k=5,
    )

    if not recommendations:
        await update.message.reply_text(
            "Рекомендаций нет, оцените больше фильмов",
            reply_markup=main_keyboard(),
        )
        return

    lines: List[str] = []
    for idx, rec in enumerate(recommendations, 1):
        title: str = movie_titles.get(rec.item_id)
        lines.append(f"{idx}. {title}\nid = {rec.item_id} | score = {rec.score:.2f}")

    await update.message.reply_text(
        "Рекомендации:\n" + "\n".join(lines),
        reply_markup=main_keyboard(),
    )


def main() -> None:
    """
    Загружает переменные окружения из .env, читает пути к файлам данных,
    и запускает бота
    """
    load_dotenv()  # загружает TELEGRAM_API_KEY, RATINGS_FILE, MOVIES_FILE из .env [web:47]

    telegram_token: str = os.getenv("TELEGRAM_API_KEY", "").strip()
    if not telegram_token:
        raise RuntimeError("TELEGRAM_API_KEY не найден в .env")

    ratings_file_path: str = os.getenv("RATINGS_FILE", "ratings.json").strip()
    movies_file_path: str = os.getenv("MOVIES_FILE", "movies.json").strip()

    movie_titles: Dict[int, str] = load_movie_titles(movies_file_path)

    application: Application = Application.builder().token(telegram_token).build()

    application.bot_data["ratings_file_path"] = ratings_file_path
    application.bot_data["movie_titles"] = movie_titles

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rate", rate_command))
    application.add_handler(CommandHandler("recommend", recommend_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
