"""
Модуль с типами данных и константами приложения.

Что я делаю?
    Определяю перечисления и константы (жанры, модели, параметры генерации).

Что я принимаю на вход?
    Ничего.

Что я возвращаю?
    Enum и константы.
"""

from enum import Enum
from typing import Dict


class MovieGenre(str, Enum):
    """
    Что я делаю?
        Определяю доступные жанры кино.

    Что я принимаю на вход?
        Ничего.

    Что я возвращаю?
        Значения жанров (str).
    """
    DRAMA = "🎭 Драма"
    DETECTIVE = "🔍 Детектив"
    COMEDY = "🎬 Комедия"
    ACTION = "🏃 Боевик"
    SCIFI = "🌈 Фантастика"
    ROMANCE = "💔 Романтика"
    THRILLER = "😱 Триллер"
    HISTORICAL = "⚔️ Исторический"


class ModelType(str, Enum):
    """
    Что я делаю?
        Определяю 2 доступные модели (по методичке): GPT и LLaMA.

    Что я принимаю на вход?
        Ничего.

    Что я возвращаю?
        Идентификаторы типа модели.
    """
    GPT = "gpt"
    LLAMA = "llama"


# МОДЕЛИ СТРОГО ИЗ МЕТОДИЧКИ [file:2]
HF_MODEL_ID_GPT: str = "ai-forever/rugpt3medium_based_on_gpt2"
HF_MODEL_ID_LLAMA: str = "meta-llama/Llama-2-7b-chat-hf"

# Жанровые подсказки
GENRE_DESCRIPTIONS: Dict[MovieGenre, str] = {
    MovieGenre.DRAMA: "серьезный и глубокий фильм с психологической глубиной",
    MovieGenre.DETECTIVE: "детективный фильм с загадками и расследованиями",
    MovieGenre.COMEDY: "легкая комедия, которая поднимет настроение",
    MovieGenre.ACTION: "динамичный боевик с экшеном и приключениями",
    MovieGenre.SCIFI: "научно-фантастический фильм с технологиями и будущим",
    MovieGenre.ROMANCE: "романтический фильм с трогательной историей любви",
    MovieGenre.THRILLER: "напряженный триллер с неожиданными поворотами",
    MovieGenre.HISTORICAL: "исторический фильм, основанный на событиях прошлого",
}

# Параметры генерации для HF Router chat/completions
# Для chat-completions (LLaMA-chat)
MAX_TOKENS: int = 260

# Для text-generation (ruGPT3)
MAX_NEW_TOKENS: int = 220
DO_SAMPLE: bool = True

TEMPERATURE: float = 0.7
TOP_P: float = 0.9
REQUEST_TIMEOUT_SEC: int = 60

