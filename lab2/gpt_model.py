"""
GPT-класс по методичке: meta-llama/Llama-3.1-8B-Instruct (через HF Router API).

Что я делаю?
    Генерирую рекомендации фильмов через HF Router chat-completion endpoint.
    Используется Llama-3.1 для GPT-класса, так как ruGPT3 и Mistral недоступны через Router.
    Различие с LLaMA-классом достигается через разные системные промпты.

Что я принимаю на вход?
    user_prompt: str

Что я возвращаю?
    str
"""

from hf_textgen_client import HFRouterClient
from app_types import HF_MODEL_ID_GPT, MAX_TOKENS_GPT, TEMPERATURE_GPT, TOP_P_GPT

class GPTModel:
    def __init__(self) -> None:
        self.client: HFRouterClient = HFRouterClient()
        self.model_id: str = HF_MODEL_ID_GPT

    async def generate_response(self, user_prompt: str) -> str:
        system_prompt: str = (
            "Ты — эксперт по кино (GPT-класс модели). Отвечай на русском. Рекомендуй реальные фильмы. "
            "Формат: Название (год), Актеры, Сюжет (2-3 предложения), Почему стоит смотреть (1-2 предложения)."
        )
        return await self.client.chat_complete(
            model_id=self.model_id,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=MAX_TOKENS_GPT,
            temperature=TEMPERATURE_GPT,
            top_p=TOP_P_GPT,
        )

