import logging
from telegram.ext import Application, CallbackQueryHandler, CommandHandler

from config import config_manager
from message_handler import MessageHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main() -> None:
    telegram_token: str = config_manager.telegram_token
    _hf_token: str = config_manager.hf_token  # проверка наличия

    handler: MessageHandler = MessageHandler()

    application: Application = Application.builder().token(telegram_token).build()
    application.add_handler(CommandHandler("start", handler.start_command_handler))
    application.add_handler(CommandHandler("help", handler.help_command_handler))
    application.add_handler(
        CallbackQueryHandler(
            handler.handle_model_selection, pattern="^model_(gpt|llama)$"
        )
    )
    application.add_handler(
        CallbackQueryHandler(handler.handle_genre_selection, pattern="^genre_")
    )

    # ВАЖНО: без await и без asyncio.run
    application.run_polling(
        allowed_updates=["message", "callback_query"],
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    main()
