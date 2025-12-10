"""
Модуль для суммаризации текста с использованием локальной модели Hugging Face.

Использует модель 'IlyaGusev/rugpt3medium_sum_gazeta' через библиотеку transformers.
Работает локально (без запросов к API).
"""

from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


def load_api_token() -> str:
    """
    Что я делаю?
        В этой версии токен не нужен, но функция оставлена для совместимости.
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        Пустую строку.
    """
    return "local_mode"


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


# Глобальные переменные для кеширования модели (чтобы не грузить каждый раз)
_model = None
_tokenizer = None
_model_name = "IlyaGusev/rugpt3medium_sum_gazeta"


def _get_model_and_tokenizer():
    """
    Что я делаю?
        Загружаю модель и токенизатор в память (Singleton).
    Что я принимаю на вход?
        Ничего.
    Что я возвращаю?
        tuple: (model, tokenizer)
    """
    global _model, _tokenizer
    if _model is None or _tokenizer is None:
        print(f"⏳ Загрузка модели {_model_name}...")
        _tokenizer = AutoTokenizer.from_pretrained(_model_name)
        _model = AutoModelForCausalLM.from_pretrained(_model_name)
        
        # Перенос на GPU если доступно
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _model.to(device)
        print(f"✅ Модель загружена на {device}")
        
    return _model, _tokenizer


def _summarize_local(
    text_input: str,
    max_length: int,
    min_length: int,
    num_beams: int = 1
) -> str:
    """
    Что я делаю?
        Генерирую саммари локально через transformers.
    Что я принимаю на вход?
        text_input (str): Текст статьи.
        max_length (int): Максимальное число токенов (не новых, а всего).
        min_length (int): Минимальное.
        num_beams (int): Число лучей.
    Что я возвращаю?
        str: Результат суммаризации.
    """
    try:
        model, tokenizer = _get_model_and_tokenizer()
        device = model.device

        # Подготовка входных данных
        tokens = tokenizer(
            text_input,
            max_length=600,  # Ограничиваем вход, чтобы не ломалась память
            add_special_tokens=False,
            truncation=True
        )["input_ids"]
        
        input_ids = torch.tensor([tokens + [tokenizer.sep_token_id]]).to(device)

        # Генерация
        output_ids = model.generate(
            input_ids=input_ids,
            max_length=max_length + input_ids.shape[1], # max_length тут - это общая длина
            min_length=min_length + input_ids.shape[1],
            num_beams=num_beams,
            no_repeat_ngram_size=4,
            early_stopping=(num_beams > 1)
        )
        
        summary = tokenizer.decode(output_ids[0], skip_special_tokens=False)
        
        # Очистка от входного текста (модель decoder-only, она продолжает текст)
        # rugpt3medium_sum_gazeta обычно генерирует после sep_token
        if tokenizer.sep_token in summary:
            parts = summary.split(tokenizer.sep_token)
            if len(parts) > 1:
                summary = parts[1]
            else:
                summary = summary  # fallback
        
        return summary.strip()

    except Exception as e:
        return f"❌ Ошибка локальной генерации: {str(e)}"


def summarize_text(
    text_input: str,
    max_length: int = 150,
    min_length: int = 50,
) -> Optional[str]:
    """
    Что я делаю?
        Выполняю базовую суммаризацию текста локально.
    Что я принимаю на вход?
        text_input (str): Исходный текст.
        max_length (int): Максимальная длина результата.
        min_length (int): Минимальная длина результата.
    Что я возвращаю?
        Optional[str]: Суммаризированный текст или сообщение об ошибке.
    """
    if not validate_text(text_input):
        return "⚠️ Текст слишком короткий! Минимум 50 символов."

    return _summarize_local(
        text_input=text_input,
        max_length=max_length,
        min_length=min_length,
        num_beams=1  # Базовый режим - жадный поиск
    )


def summarize_text_advanced(
    text_input: str,
    max_length: int = 150,
    min_length: int = 50,
    num_beams: int = 4,
) -> Optional[str]:
    """
    Что я делаю?
        Выполняю расширенную суммаризацию (beam search).
    Что я принимаю на вход?
        text_input (str): Исходный текст.
        max_length (int): Максимальная длина.
        min_length (int): Минимальная длина.
        num_beams (int): Количество лучей.
    Что я возвращаю?
        Optional[str]: Суммаризированный текст или сообщение об ошибке.
    """
    if not validate_text(text_input):
        return "⚠️ Текст слишком короткий! Минимум 50 символов."

    return _summarize_local(
        text_input=text_input,
        max_length=max_length,
        min_length=min_length,
        num_beams=num_beams
    )
