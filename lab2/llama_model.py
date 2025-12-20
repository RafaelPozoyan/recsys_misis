"""
Модуль "LLaMA": Llama-3.1-8B-Instruct. Генерирует рекомендации фильмов.
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
        """Генерирует рекомендацию фильма на основе запроса.

        Args:
            user_prompt: Текст запроса пользователя

        Returns:
            Строка с ответом модели в формате текстовой рекомендации фильма.
        """
        system_prompt: str = (
            "You are a movie expert assistant. Answer in Russian. "
            "Recommend one real movie with: Название (год), актеры, сюжет, почему стоит смотреть"
        )
        return await self.client.chat_complete(
            model_id=self.model_id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=MAX_TOKENS_LLAMA,
            temperature=TEMPERATURE_LLAMA,
            top_p=TOP_P_LLAMA,
        )
