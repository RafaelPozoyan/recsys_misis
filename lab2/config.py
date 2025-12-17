"""
Модуль для управления конфигурацией и переменными окружения.

Что я делаю?
    Загружаю переменные окружения из .env и предоставляю доступ к токенам.

Что я принимаю на вход?
    - Путь к .env (по умолчанию ".env")

Что я возвращаю?
    - Значения переменных окружения через свойства ConfigManager.
"""

import os
from typing import Optional
from dotenv import load_dotenv


class ConfigManager:
    """
    Что я делаю?
        Загружаю конфигурацию из .env и предоставляю удобный доступ к токенам.

    Что я принимаю на вход?
        env_path: str - путь к .env

    Что я возвращаю?
        Свойства с токенами (str).
    """

    def __init__(self, env_path: str = ".env") -> None:
        """
        Что я делаю?
            Загружаю .env в переменные окружения.

        Что я принимаю на вход?
            env_path: str

        Что я возвращаю?
            None
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
