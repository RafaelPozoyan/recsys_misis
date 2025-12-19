"""
Модуль "LLaMA" по методичке: Llama-3.1-8B-Instruct (через HF Router API).

Что я делаю?
    Генерирую рекомендации фильмов, используя модель LLaMA-класса из методички.

Что я принимаю на вход?
    - Промпт пользователя (str)

Что я возвращаю?
    - Сгенерированный ответ (str)
"""

from typing import Any, Dict

from hf_textgen_client import HFRouterClient
from app_types import (
    HF_MODEL_ID_LLAMA,
    MAX_TOKENS_LLAMA,
    TEMPERATURE_LLAMA,
    TOP_P_LLAMA,
)


class LLaMAModel:
    def __init__(self) -> None:
        self.client: HFRouterClient = HFRouterClient()
        self.model_id: str = HF_MODEL_ID_LLAMA

    async def generate_response(self, user_prompt: str) -> str:
        system_prompt: str = (
            "You are a movie expert assistant. Answer in Russian. "
            "Recommend one real movie with: Название (год), Актеры, Сюжет, Почему стоит смотреть."
        )
        return await self.client.chat_complete(
            model_id=self.model_id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=MAX_TOKENS_LLAMA,
            temperature=TEMPERATURE_LLAMA,
            top_p=TOP_P_LLAMA,
        )
