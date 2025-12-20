import os
from typing import Optional
from dotenv import load_dotenv


class ConfigManager:
    """
    Загружает конфигурацию из .env

    Args:
        env_path: str - путь к .env

    Returns:
        Свойства с токенами (str).
    """

    def __init__(self, env_path: str = ".env") -> None:
        """
        Загружаtn .env в переменные окружения.

        Args:
            env_path: str
        """
        load_dotenv(env_path)

    @property
    def telegram_token(self) -> str:
        """
        Что я делаю?
            Достаю TELEGRAM_TOKEN из окружения.

        Что я принимаю на вход?
            Ничего.

        Что я возвращаю?
            str: токен Telegram-бота.
        """
        token: Optional[str] = os.getenv("TELEGRAM_TOKEN")
        if not token:
            raise ValueError("TELEGRAM_TOKEN не найден в .env")
        return token

    @property
    def hf_token(self) -> str:
        """
        Что я делаю?
            Достаю HF_TOKEN из окружения.

        Что я принимаю на вход?
            Ничего.

        Что я возвращаю?
            str: токен Hugging Face (Inference API).
        """
        token: Optional[str] = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError("HF_TOKEN не найден в .env")
        return token


config_manager: ConfigManager = ConfigManager()
