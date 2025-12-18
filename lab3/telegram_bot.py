from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from cf_user_cosine import UserBasedCosineCF, Recommendation
from storage_json import load_ratings, save_ratings, upsert_rating, RatingTriplet


@dataclass(frozen=True)
class AppConfig:
    """
    Что я делаю?
        Храню настройки приложения (токен и путь к файлу с оценками).

    Что я принимаю на вход?
        telegram_token: токен Telegram бота.
        ratings_file_path: путь к JSON с оценками.

    Что я возвращаю?
        Экземпляр AppConfig.
    """
    telegram_token: str
    ratings_file_path: str


def load_config() -> AppConfig:
    """
    Что я делаю?
        Загружаю конфигурацию из переменных окружения (.env).

    Что я принимаю на вход?
        None.

    Что я возвращаю?
        AppConfig с токеном и путём к файлу оценок.
    """
    load_dotenv()
    telegram_token: str = os.getenv("TELEGRAM_API_KEY", "").strip()
    ratings_file_path: str = os.getenv("RATINGS_FILE", "ratings.json").strip()

    if not telegram_token:
        raise RuntimeError("TELEGRAM_API_KEY не найден в переменных окружения (.env).")

    return AppConfig(telegram_token=telegram_token, ratings_file_path=ratings_file_path)


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
        "Привет! Это User-Based CF бот (cosine similarity).\n"
        "Команды:\n"
        "/rate <item_id> <rating> — поставить оценку (1..5)\n"
        "/recommend — рекомендации\n"
        "/myratings — мои оценки\n"
        "/help — помощь"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Что я делаю?
        Отправляю справку.

    Что я принимаю на вход?
        update: объект Telegram Update.
        context: контекст обработчика.

    Что я возвращаю?
        Ничего (None).
    """
    if update.message is None:
        return

    await update.message.reply_text(
        "Примеры:\n"
        "/rate 10 5\n"
        "/rate 11 3.5\n"
        "/recommend\n"
        "/myratings"
    )


async def rate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Что я делаю?
        Принимаю оценку и сохраняю её в файл.

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
        await update.message.reply_text("Формат: /rate <item_id> <rating>")
        return

    try:
        item_id: int = int(args[0])
        rating_value: float = float(args[1])
    except ValueError:
        await update.message.reply_text("Ошибка: item_id должен быть int, rating — число.")
        return

    if rating_value < 1.0 or rating_value > 5.0:
        await update.message.reply_text("Ошибка: rating должен быть в диапазоне 1..5.")
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

    await update.message.reply_text(f"Сохранено: item {item_id} = {rating_value:.1f}")


async def myratings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Что я делаю?
        Показываю пользователю его оценки.

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
    user_ratings: List[RatingTriplet] = [triplet for triplet in all_ratings if triplet[0] == user_id]

    if not user_ratings:
        await update.message.reply_text("У вас пока нет оценок. Добавьте: /rate <item_id> <rating>")
        return

    lines: List[str] = [f"{item_id}: {rating:.1f}" for _, item_id, rating in sorted(user_ratings, key=lambda t: t[1])]
    await update.message.reply_text("Ваши оценки:\n" + "\n".join(lines))


async def recommend_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Что я делаю?
        Строю рекомендации по User-Based CF (cosine) и отправляю их пользователю.

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
    if len(all_ratings) < 5:
        await update.message.reply_text("Мало данных для рекомендаций: пусть разные пользователи поставят больше оценок.")
        return

    model: UserBasedCosineCF = UserBasedCosineCF(ratings=all_ratings)
    recommendations: List[Recommendation] = model.recommend_items(
        target_user_id=user_id,
        neighbors_k=10,
        recommendations_k=5,
    )

    if not recommendations:
        await update.message.reply_text("Рекомендаций нет. Оцените больше объектов или дождитесь других пользователей.")
        return

    lines: List[str] = [f"{idx}. item {rec.item_id} (score={rec.score:.2f})" for idx, rec in enumerate(recommendations, 1)]
    await update.message.reply_text("Рекомендации:\n" + "\n".join(lines))


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
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("rate", rate_command))
    application.add_handler(CommandHandler("myratings", myratings_command))
    application.add_handler(CommandHandler("recommend", recommend_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
