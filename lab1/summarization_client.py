from __future__ import annotations

import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv


class RapidApiArticleSummarizerClient:
    """
    1) Что я делаю?
       Класс инкапсулирует обращение к RapidAPI Article Extractor and Summarizer:
       отправляет HTTP‑запрос по URL статьи и получает её краткое резюме.

    2) Что я принимаю на вход?
       - В конструктор: имена переменных окружения с ключом и host'ом.
       - В summarize_article: строку с URL статьи и язык суммаризации.

    3) Что я возвращаю?
       - Метод summarize_article возвращает строку с суммаризацией статьи.
    """

    def __init__(
        self,
        api_key_env_var: str = "RAPIDAPI_KEY",
        api_host_env_var: str = "RAPIDAPI_HOST",
    ) -> None:
        load_dotenv()

        api_key: str | None = os.getenv(api_key_env_var)
        api_host: str | None = os.getenv(api_host_env_var)

        if api_key is None or api_key.strip() == "":
            raise ValueError(
                f"API‑ключ не найден в переменной окружения {api_key_env_var}"
            )

        if api_host is None or api_host.strip() == "":
            raise ValueError(
                f"Host API не найден в переменной окружения {api_host_env_var}"
            )

        self._api_key: str = api_key
        self._api_host: str = api_host
        # endpoint для Article Extractor and Summarizer
        self._endpoint_url: str = (
            "https://article-extractor-and-summarizer.p.rapidapi.com/summarize"
        )

    def _build_headers(self) -> Dict[str, str]:
        """
        1) Что я делаю?
           Формирую HTTP‑заголовки для запроса к RapidAPI.

        2) Что я принимаю на вход?
           - Ничего не принимаю.

        3) Что я возвращаю?
           - Словарь заголовков.
        """
        headers: Dict[str, str] = {
            "x-rapidapi-key": self._api_key,
            "x-rapidapi-host": self._api_host,
        }
        return headers

    def _build_query_params(self, article_url: str, summary_language: str) -> Dict[str, str]:
        """
        1) Что я делаю?
           Формирую query‑параметры для запроса API.

        2) Что я принимаю на вход?
           - article_url: URL статьи, которую нужно извлечь и суммаризировать.
           - summary_language: язык, на котором нужен summary (например, 'en').

        3) Что я возвращаю?
           - Словарь с query‑параметрами.
        """
        params: Dict[str, str] = {
            "url": article_url,
            "length": "3",        # пример: короткое резюме (можно менять на 'short', 'medium', 'long' — см. доку)
            "lang": summary_language,
        }
        return params

    def summarize_article(self, article_url: str, summary_language: str = "en") -> str:
        """
        1) Что я делаю?
           Отправляю GET‑запрос к Article Extractor and Summarizer,
           получаю JSON‑ответ и извлекаю текст суммаризации.

        2) Что я принимаю на вход?
           - article_url: строка с URL статьи.
           - summary_language: код языка суммаризации (по умолчанию 'en').

        3) Что я возвращаю?
           - Строку с итоговой суммаризацией.
        """
        if not article_url.strip():
            raise ValueError("URL статьи не может быть пустым.")

        headers: Dict[str, str] = self._build_headers()
        params: Dict[str, str] = self._build_query_params(
            article_url=article_url,
            summary_language=summary_language,
        )

        response: requests.Response = requests.get(
            self._endpoint_url,
            headers=headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        response_data: Dict[str, Any] = response.json()

        # Фактический формат ответа этого API (проверено по playground):
        # {
        #   "summary": "....",
        #   "title": "....",
        #   "url": "....",
        #   ...
        # }
        summary: Any = response_data.get("summary")

        if not isinstance(summary, str):
            raise RuntimeError(
                f"Не удалось извлечь поле 'summary' из ответа API: {response_data}"
            )

        return summary
