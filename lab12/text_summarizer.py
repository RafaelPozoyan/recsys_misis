"""
Модуль для суммаризации текста с использованием Hugging Face API.

Использует бесплатный сервис Hugging Face Inference API для создания
кратких резюме текстов на русском языке.
"""

import os
from typing import Optional, Any, Dict

import requests
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()


def load_api_token() -> str:
    """
    Что я делаю?
        Загружаю API токен для Hugging Face из переменной окружения.
    Что я принимаю на вход?
        Ничего не принимаю, использую переменную окружения HUGGINGFACE_API_TOKEN.
    Что я возвращаю?
        Строку с API токеном.

    Raises:
        ValueError: Если токен не найден в переменных окружения.
    """
    api_token: str = os.getenv("HUGGINGFACE_API_TOKEN", "").strip()
    if not api_token:
        raise ValueError(
            "❌ API токен не найден! "
            "Установите переменную окружения HUGGINGFACE_API_TOKEN в файле .env"
        )
    return api_token


def validate_text(text_input: str) -> bool:
    """
    Что я делаю?
        Проверяю, что входной текст имеет минимальную длину для суммаризации.
    Что я принимаю на вход?
        text_input (str): Текст для проверки.
    Что я возвращаю?
        bool: True если текст достаточно длинный, False иначе.
    """
    minimum_length: int = 50
    return len(text_input.strip()) >= minimum_length


# одна русская модель суммаризации
HF_MODEL_NAME: str = "IlyaGusev/rugpt3medium_sum_gazeta"
HF_ROUTER_URL: str = "https://router.huggingface.co/hf-inference"


def _call_hf_api(
    text_input: str,
    max_length: int,
    min_length: int,
    extra_params: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Что я делаю?
        Вызываю Hugging Face router Inference API для выбранной модели.
    Что я принимаю на вход?
        text_input (str): Исходный текст.
        max_length (int): Максимальная длина вывода (в новых токенах).
        min_length (int): Минимальная длина вывода (в новых токенах).
        extra_params (dict | None): Дополнительные параметры генерации.
    Что я возвращаю?
        str: Суммаризированный текст или сообщение об ошибке.
    """
    api_token: str = load_api_token()

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    params: Dict[str, Any] = {
        "max_new_tokens": max_length,
        "min_new_tokens": min_length,
    }
    if extra_params:
        params.update(extra_params)

    payload: Dict[str, Any] = {
        "model": HF_MODEL_NAME,
        "inputs": text_input,
        "parameters": params,
    }

    try:
        response: requests.Response = requests.post(
            HF_ROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        result: Any = response.json()

        # router API обычно возвращает список словарей с полем generated_text
        if isinstance(result, list) and result:
            item: Any = result[0]
            if isinstance(item, dict) and "generated_text" in item:
                summary: str = str(item["generated_text"]).strip()
                if summary:
                    return summary

        return f"❌ Ошибка обработки ответа: {result}"

    except requests.exceptions.Timeout:
        return "⏱️ Ошибка: запрос истек по времени. Попробуйте позже."
    except requests.exceptions.ConnectionError:
        return "🌐 Ошибка: проблема с подключением к интернету."
    except requests.exceptions.HTTPError:
        return f"❌ HTTP ошибка {response.status_code}: {response.text}"
    except requests.exceptions.RequestException as req_err:
        return f"❌ Ошибка запроса: {str(req_err)}"
    except ValueError:
        return "❌ Ошибка: некорректный ответ от сервера (не JSON)."


def summarize_text(
    text_input: str,
    max_length: int = 150,
    min_length: int = 50,
) -> Optional[str]:
    """
    Что я делаю?
        Выполняю базовую суммаризацию текста через Hugging Face router API.
    Что я принимаю на вход?
        text_input (str): Исходный текст.
        max_length (int): Максимальная длина результата (новые токены).
        min_length (int): Минимальная длина результата (новые токены).
    Что я возвращаю?
        Optional[str]: Суммаризированный текст или сообщение об ошибке.
    """
    if not validate_text(text_input):
        return "⚠️ Текст слишком короткий! Минимум 50 символов."

    return _call_hf_api(
        text_input=text_input,
        max_length=max_length,
        min_length=min_length,
    )


def summarize_text_advanced(
    text_input: str,
    max_length: int = 150,
    min_length: int = 50,
    num_beams: int = 4,
) -> Optional[str]:
    """
    Что я делаю?
        Выполняю расширенную суммаризацию с дополнительными параметрами.
    Что я принимаю на вход?
        text_input (str): Исходный текст.
        max_length (int): Максимальная длина результата.
        min_length (int): Минимальная длина результата.
        num_beams (int): Количество лучей для beam search.
    Что я возвращаю?
        Optional[str]: Суммаризированный текст или сообщение об ошибке.
    """
    if not validate_text(text_input):
        return "⚠️ Текст слишком короткий! Минимум 50 символов."

    return _call_hf_api(
        text_input=text_input,
        max_length=max_length,
        min_length=min_length,
        extra_params={
            "num_beams": num_beams,
            "early_stopping": True,
        },
    )
