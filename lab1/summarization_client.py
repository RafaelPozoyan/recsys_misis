import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


def _get_api_headers() -> Dict[str, str]:
    """
    Функция для получения заголовков

    Returns:
        Dict[str, str]: Словарь, содержащий API-ключ, хост и тип контента для запроса.
    """
    api_key: Optional[str] = os.getenv("RAPIDAPI_KEY")
    api_host: Optional[str] = os.getenv("RAPIDAPI_HOST")

    return {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": api_host,
    }


def get_article_summary(url: str, sentences_count: int = 1) -> str:
    """
    Отправляет GET запрос с URL статьи и параметром длины

    Args:
        url: URL статьи.
        sentences_count: Количество предложений в суммаризации.

    Returns:
        str: Суммаризированный текст.
    """
    endpoint_url: str = (
        "https://article-extractor-and-summarizer.p.rapidapi.com/summarize"
    )

    # Передаем параметр length в API
    querystring: Dict[str, str] = {
        "url": url,
        "lang": "ru",
        "length": str(sentences_count),
    }

    response: requests.Response = requests.get(
        endpoint_url, headers=_get_api_headers(), params=querystring
    )

    response.raise_for_status()
    data: Dict[str, Any] = response.json()

    return data.get("summary", f"Ошибка: {data}")


def get_text_summary(text: str, sentences_count: int = 1) -> str:
    """
    Отправляет POST запрос с текстом и параметром длины

    Args:
        text: Текст статьи
        sentences_count: Количество предложений в суммаризации

    Returns:
        str: Суммаризированный текст
    """
    endpoint_url: str = (
        "https://article-extractor-and-summarizer.p.rapidapi.com/summarize-text"
    )

    querystring: Dict[str, Any] = {
        "text": text,
        "lang": "ru",
        "length": str(sentences_count),
    }

    response: requests.Response = requests.post(
        endpoint_url, json=querystring, headers=_get_api_headers()
    )

    response.raise_for_status()
    data: Dict[str, Any] = response.json()

    return data.get("summary", f"Ошибка: {data}")
