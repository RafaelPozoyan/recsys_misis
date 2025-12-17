"""
Универсальный асинхронный клиент Hugging Face Router API.

Что я делаю?
    Поддерживаю два режима:
    1) Chat Completion: https://router.huggingface.co/v1/chat/completions
    2) Text Generation: https://router.huggingface.co/v1/completions

Что я принимаю на вход?
    - HF токен
    - model_id
    - prompt/messages
    - параметры генерации

Что я возвращаю?
    - str: сгенерированный текст
"""

import asyncio
from typing import Any, Dict, Optional

import aiohttp

from config import config_manager
from app_types import REQUEST_TIMEOUT_SEC


class HFRouterClient:
    """
    Что я делаю?
        Даю методы chat_complete и text_generate для разных типов моделей.

    Что я принимаю на вход?
        hf_token: Optional[str]

    Что я возвращаю?
        Методы для генерации текста.
    """

    CHAT_URL: str = "https://router.huggingface.co/v1/chat/completions"
    COMPLETIONS_URL: str = "https://router.huggingface.co/v1/completions"

    def __init__(self, hf_token: Optional[str] = None) -> None:
        """
        Что я делаю?
            Сохраняю HF токен.

        Что я принимаю на вход?
            hf_token: Optional[str]

        Что я возвращаю?
            None
        """
        self.hf_token: str = hf_token or config_manager.hf_token

    def _headers(self) -> Dict[str, str]:
        """
        Что я делаю?
            Формирую заголовки авторизации.

        Что я принимаю на вход?
            Ничего.

        Что я возвращаю?
            Dict[str, str]
        """
        return {
            "Authorization": f"Bearer {self.hf_token}",
            "Content-Type": "application/json",
        }

    def _textgen_url(self) -> str:
        """
        Что я делаю?
            Возвращаю URL для text-generation (через router API completions endpoint).

        Что я принимаю на вход?
            Ничего.

        Что я возвращаю?
            str
        """
        return self.COMPLETIONS_URL

    async def chat_complete(
        self,
        model_id: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
    ) -> str:
        """
        Что я делаю?
            Делаю запрос Chat Completion (для chat-моделей типа LLaMA-2-chat).

        Что я принимаю на вход?
            model_id, system_prompt, user_prompt, max_tokens, temperature, top_p

        Что я возвращаю?
            str: message.content
        """
        payload: Dict[str, Any] = {
            "model": model_id,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False,
        }
        return await self._post_json(self.CHAT_URL, payload, mode="chat")

    async def text_generate(
        self,
        model_id: str,
        prompt: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float,
        do_sample: bool,
    ) -> str:
        """
        Что я делаю?
            Делаю запрос Text Generation через completions endpoint (для non-chat моделей типа ruGPT3).

        Что я принимаю на вход?
            model_id: str
            prompt: str
            max_new_tokens: int
            temperature: float
            top_p: float
            do_sample: bool

        Что я возвращаю?
            str: generated_text
        """
        payload: Dict[str, Any] = {
            "model": model_id,
            "prompt": prompt,
            "max_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "stream": False,
        }
        url: str = self._textgen_url()
        return await self._post_json(url, payload, mode="completions")

    async def _post_json(self, url: str, payload: Dict[str, Any], mode: str) -> str:
        """
        Что я делаю?
            Отправляю POST и парсю ответ в зависимости от режима.

        Что я принимаю на вход?
            url: str
            payload: Dict[str, Any]
            mode: str ("chat" | "textgen")

        Что я возвращаю?
            str
        """
        timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=REQUEST_TIMEOUT_SEC)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=self._headers(), json=payload) as resp:
                    if resp.status == 503:
                        data_503: Any = await resp.json()
                        wait_time: float = float(data_503.get("estimated_time", 8.0))
                        await asyncio.sleep(wait_time)
                        async with session.post(url, headers=self._headers(), json=payload) as resp2:
                            return await self._parse(resp2, mode)

                    return await self._parse(resp, mode)

        except asyncio.TimeoutError as e:
            raise TimeoutError("HF Router: превышен таймаут") from e
        except aiohttp.ClientError as e:
            raise RuntimeError(f"HF Router: ошибка сети: {e}") from e

    async def _parse(self, response: aiohttp.ClientResponse, mode: str) -> str:
        """
        Что я делаю?
            Парсю JSON ответа.

        Что я принимаю на вход?
            response: aiohttp.ClientResponse
            mode: str

        Что я возвращаю?
            str
        """
        if response.status != 200:
            text: str = await response.text()
            raise RuntimeError(f"HF Router ошибка {response.status}: {text}")

        data: Any = await response.json()

        if mode == "chat":
            content: Optional[str] = (
                data.get("choices", [{}])[0].get("message", {}).get("content")
            )
            if not content:
                raise RuntimeError(f"Неожиданный формат chat-ответа: {data}")
            return content.strip()

        # mode == "completions" (для text generation)
        if mode == "completions":
            content: Optional[str] = (
                data.get("choices", [{}])[0].get("text")
            )
            if content is not None:
                return content.strip()
            raise RuntimeError(f"Неожиданный формат completions-ответа: {data}")

        # mode == "textgen" (старый формат, оставлен для совместимости)
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            generated: Optional[str] = data[0].get("generated_text")
            if generated:
                return generated.strip()

        raise RuntimeError(f"Неожиданный формат ответа: {data}")
