from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List

from dotenv import load_dotenv
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, ContextTypes

from cf_user_cosine import Recommendation, UserBasedCosineCF
from storage_json import RatingTriplet, load_ratings, save_ratings, upsert_rating


@dataclass(frozen=True)
class AppConfig:
    """
    Что я делаю?
        Храню настройки приложения (токен и пути к файлам с данными).

    Что я принимаю на вход?
        telegram_token: Токен Telegram бота.
        ratings_file_path: Путь к JSON с оценками (ratings.json).
        movies_file_path: Путь к JSON с названиями фильмов (movies.json).

    Что я возвращаю?
        Экземпляр AppConfig.
    """
    telegram_token: str
    ratings_file_path: str
    movies_file_path: str


def load_config() -> AppConfig:
    """
    Что я делаю?
        Загружаю конфигурацию из переменных окружения (.env).

    Что я принимаю на вход?
        None.

    Что я возвращаю?
        AppConfig с токеном и путями к файлам.
    """
    load_dotenv()

    telegram_token: str = os.getenv("TELEGRAM_API_KEY", "").strip()
    ratings_file_path: str = os.getenv("RATINGS_FILE", "ratings.json").strip()
    movies_file_path: str = os.getenv("MOVIES_FILE", "movies.json").strip()

    if not telegram_token:
        raise RuntimeError("TELEGRAM_API_KEY не найден в переменных окружения (.env).")

    return AppConfig(
        telegram_token=telegram_token,
        ratings_file_path=ratings_file_path,
        movies_file_path=movies_file_path,
    )


def main_keyboard() -> ReplyKeyboardMarkup:
    """
    Что я делаю?
        Создаю клавиатуру с кнопками-командами.

    Что я принимаю на вход?
        None.

    Что я возвращаю?
        ReplyKeyboardMarkup для Telegram.
    """
    keyboard: List[List[KeyboardButton]] = [
        [KeyboardButton("/recommend"), KeyboardButton("/myratings")],
        [KeyboardButton("/start")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)


def load_movie_titles(movies_file_path: str) -> Dict[int, str]:
    """
    Что я делаю?
        Загружаю отображение movie_id -> movie_title из movies.json.

    Что я принимаю на вход?
        movies_file_path: Путь к файлу movies.json.

    Что я возвращаю?
        Словарь, где ключи — int movie_id, значения — названия фильмов.
    """
    if not os.path.exists(movies_file_path):
        return {}

    with open(movies_file_path, "r", encoding="utf-8") as file:
        raw: Dict[str, str] = json.load(file)

    # В JSON ключи всегда строки, поэтому приводим к int
    return {int(movie_id): title for movie_id, title in raw.items()}


def format_movie_name(movie_titles: Dict[int, str], movie_id: int) -> str:
    """
    Что я делаю?
        Формирую “человеческое” имя фильма по movie_id.

    Что я принимаю на вход?
        movie_titles: Словарь {movie_id: title}.
        movie_id: ID фильма.

    Что я возвращаю?
        Название фильма или заглушку "Фильм #id".
    """
    return movie_titles.get(movie_id, f"Фильм #{movie_id}")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Что я делаю?
        Отправляю приветствие и команды.

    Что я принимаю на вход?
        update: объект Telegram Update.
        context: контекст обработчика.

    Что я возвращаю?
        Ничего (None).
    """
    if update.message is None:
        return

    await update.message.reply_text(
        "Привет. Я — бот, рекомендующий фильмы по косинусному сходству (User-Based CF).\n\n"
        "Меня создал студент группы БПМ-22-ПО-3 Позоян Рафаэль.\n\n"
        "Команды:\n"
        "/rate <id фильма> <рейтинг> — рейтинг от 1 до 5\n"
        "/recommend — рекомендации\n"
        "/myratings — мои оценки\n",
        reply_markup=main_keyboard(),
    )


async def rate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Что я делаю?
        Принимаю оценку и сохраняю её в файл ratings.json.

    Что я принимаю на вход?
        update: объект Telegram Update.
        context: контекст обработчика (context.args).

    Что я возвращаю?
        Ничего (None).
    """


    if update.message is None:
        return

    args: List[str] = list(context.args)
    if len(args) != 2:
        await update.message.reply_text("Формат: /rate <id фильма> <rating>", reply_markup=main_keyboard())
        return

    try:
        item_id: int = int(args[0])
        rating_value: float = float(args[1])
    except ValueError:
        await update.message.reply_text("Ошибка: id фильма должен быть int, rating — число.", reply_markup=main_keyboard())
        return

    if rating_value < 1.0 or rating_value > 5.0:
        await update.message.reply_text("Ошибка: rating должен быть в диапазоне 1..5.", reply_markup=main_keyboard())
        return

    config: AppConfig = load_config()
    user_id: int = int(update.effective_user.id)

    current_ratings: List[RatingTriplet] = load_ratings(config.ratings_file_path)
    updated_ratings: List[RatingTriplet] = upsert_rating(
        ratings=current_ratings,
        user_id=user_id,
        item_id=item_id,
        rating=rating_value,
    )
    save_ratings(config.ratings_file_path, updated_ratings)

    await update.message.reply_text(
        f"Сохранено: id = {item_id} | Рейтинг = {rating_value:.1f}",
        reply_markup=main_keyboard(),
    )


async def myratings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Что я делаю?
        Показываю пользователю его оценки (с названиями фильмов, если есть movies.json).

    Что я принимаю на вход?
        update: объект Telegram Update.
        context: контекст обработчика.

    Что я возвращаю?
        Ничего (None).
    """
    if update.message is None:
        return

    config: AppConfig = load_config()
    user_id: int = int(update.effective_user.id)

    movie_titles: Dict[int, str] = load_movie_titles(config.movies_file_path)

    all_ratings: List[RatingTriplet] = load_ratings(config.ratings_file_path)
    user_ratings: List[RatingTriplet] = [triplet for triplet in all_ratings if triplet[0] == user_id]

    if not user_ratings:
        await update.message.reply_text(
            "У вас пока нет оценок. Добавьте: /rate <id фильма> <rating>",
            reply_markup=main_keyboard(),
        )
        return

    user_ratings_sorted: List[RatingTriplet] = sorted(user_ratings, key=lambda t: t[1])

    lines: List[str] = []
    for _, item_id, rating in user_ratings_sorted:
        title: str = format_movie_name(movie_titles, item_id)
        lines.append(f"{title} \nid фильма = {item_id} | Рейтинг = {rating:.1f} \n{'='*10}")

    await update.message.reply_text("Ваши оценки:\n" + "\n".join(lines), reply_markup=main_keyboard())


async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Что я делаю?
        Строю рекомендации по User-Based CF (cosine) и отправляю их пользователю,
        добавляя названия фильмов из movies.json.

    Что я принимаю на вход?
        update: объект Telegram Update.
        context: контекст обработчика.

    Что я возвращаю?
        Ничего (None).
    """
    if update.message is None:
        return

    config: AppConfig = load_config()
    user_id: int = int(update.effective_user.id)

    all_ratings: List[RatingTriplet] = load_ratings(config.ratings_file_path)
    if len(all_ratings) < 3:
        await update.message.reply_text(
            "Похоже, ты не загрузил датасет",
            reply_markup=main_keyboard(),
        )
        return

    movie_titles: Dict[int, str] = load_movie_titles(config.movies_file_path)

    model: UserBasedCosineCF = UserBasedCosineCF(ratings=all_ratings)
    recommendations: List[Recommendation] = model.recommend_items(
        target_user_id=user_id,
        neighbors_k=10,
        recommendations_k=5,
    )

    if not recommendations:
        await update.message.reply_text(
            "Рекомендаций нет. Оцените больше фильмов или дождитесь других пользователей.",
            reply_markup=main_keyboard(),
        )
        return

    lines: List[str] = []
    for idx, rec in enumerate(recommendations, 1):
        title: str = format_movie_name(movie_titles, rec.item_id)
        lines.append(f"{idx}. {title} \n Рейтинг={rec.score:.2f}")

    await update.message.reply_text("Рекомендации:\n" + "\n".join(lines), reply_markup=main_keyboard())


def main() -> None:
    """
    Что я делаю?
        Запускаю асинхронный Telegram-бот (polling) и регистрирую команды.

    Что я принимаю на вход?
        None.

    Что я возвращаю?
        Ничего (None).
    """
    config: AppConfig = load_config()

    application: Application = Application.builder().token(config.telegram_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("rate", rate_command))
    application.add_handler(CommandHandler("myratings", myratings_command))
    application.add_handler(CommandHandler("recommend", recommend_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
