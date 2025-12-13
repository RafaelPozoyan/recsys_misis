import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

def _get_api_headers() -> Dict[str, str]:
    """Вспомогательная функция для получения заголовков."""
    api_key: Optional[str] = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        raise ValueError("API ключ не найден. Проверьте файл .env")
    
    return {
        "content-type": "application/json",
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "article-extractor-and-summarizer.p.rapidapi.com"
    }

def get_article_summary(url: str, sentences_count: int = 3) -> str:
    """
    Получает суммаризацию по URL с заданным количеством предложений.

    1) Что я делаю? Отправляю GET запрос с URL статьи и параметром длины.
    2) Что я принимаю? Ссылку (str) и кол-во предложений (int).
    3) Что я возвращаю? Суммаризированный текст (str).
    """
    endpoint_url: str = "https://article-extractor-and-summarizer.p.rapidapi.com/summarize"
    
    # Передаем параметр length в API
    querystring: Dict[str, str] = {
        "url": url,
        "lang": "ru",
        "length": str(sentences_count) 
    }

    headers = _get_api_headers()
    if "content-type" in headers:
        del headers["content-type"]

    response: requests.Response = requests.get(
        endpoint_url, 
        headers=headers, 
        params=querystring
    )
    
    response.raise_for_status()
    data: Dict[str, Any] = response.json()
    
    return data.get("summary", f"Ошибка: {data}")

def get_text_summary(text: str, sentences_count: int = 3) -> str:
    """
    Получает суммаризацию по тексту с заданным количеством предложений.

    1) Что я делаю? Отправляю POST запрос с текстом и параметром длины.
    2) Что я принимаю? Текст (str) и кол-во предложений (int).
    3) Что я возвращаю? Суммаризированный текст (str).
    """
    endpoint_url: str = "https://article-extractor-and-summarizer.p.rapidapi.com/summarize-text"
    
    payload: Dict[str, Any] = {
        "text": text,
        "lang": "ru",
        "length": str(sentences_count)
    }

    response: requests.Response = requests.post(
        endpoint_url, 
        json=payload, 
        headers=_get_api_headers()
    )

    response.raise_for_status()
    data: Dict[str, Any] = response.json()
    
    return data.get("summary", f"Ошибка: {data}")
