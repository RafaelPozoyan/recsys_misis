"""
GPT-класс по методичке: ai-forever/rugpt3medium_based_on_gpt2.

Что я делаю?
    Делаю chat-completion запрос через HF Router и возвращаю ответ.

Что я принимаю на вход?
    user_prompt: str

Что я возвращаю?
    str
"""

from hf_textgen_client import HFRouterClient
from app_types import HF_MODEL_ID_GPT, MAX_NEW_TOKENS, TEMPERATURE, TOP_P, DO_SAMPLE

class GPTModel:
    def __init__(self) -> None:
        self.client: HFRouterClient = HFRouterClient()
        self.model_id: str = HF_MODEL_ID_GPT

    async def generate_response(self, user_prompt: str) -> str:
        prompt: str = (
            "Ты — эксперт по кино. Отвечай на русском. Рекомендуй реальные фильмы.\n"
            "Формат:\n"
            "Название (год)\n"
            "Актеры: ...\n"
            "Сюжет: 2-3 предложения.\n"
            "Почему стоит смотреть: 1-2 предложения.\n\n"
            f"Запрос: {user_prompt}\n"
        )
        return await self.client.text_generate(
            model_id=self.model_id,
            prompt=prompt,
            max_new_tokens=MAX_NEW_TOKENS,
            temperature=TEMPERATURE,
            top_p=TOP_P,
            do_sample=DO_SAMPLE,
        )

