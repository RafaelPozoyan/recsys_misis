"""
Модуль с типами данных и константами приложения.
Определяет перечисления и константы (жанры, модели, параметры генерации).
"""

from enum import Enum
from typing import Dict


class MovieGenre(str, Enum):
    """
    Определяет жанры кино.

    Returns:
        Значения жанров (str).
    """

    DRAMA = "Драма"
    DETECTIVE = "Детектив"
    COMEDY = "Комедия"
    ACTION = "Боевик"
    SCIFI = "Фантастика"
    ROMANCE = "Романтика"
    THRILLER = "Триллер"
    HISTORICAL = "Исторический"


class ModelType(str, Enum):
    """
    Определяет 2 доступные модели: GPT и LLaMA.

    Returns:
        Идентификаторы типа модели.
    """

    GPT = "gpt"
    LLAMA = "llama"


HF_MODEL_ID_GPT: str = "meta-llama/Llama-3.1-8B-Instruct"
HF_MODEL_ID_LLAMA: str = "meta-llama/Llama-3.1-8B-Instruct"

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
MAX_TOKENS_LLAMA: int = 260
TEMPERATURE_LLAMA: float = 0.7
TOP_P_LLAMA: float = 0.9

# Для chat-completions (GPT через Llama-3.1)
# Используем другие параметры для создания различия в поведении
MAX_TOKENS_GPT: int = 220
TEMPERATURE_GPT: float = 0.8  # Более креативные ответы
TOP_P_GPT: float = 0.95  # Более разнообразные ответы

# Общие параметры
MAX_NEW_TOKENS: int = 220
DO_SAMPLE: bool = True
TEMPERATURE: float = 0.7
TOP_P: float = 0.9
REQUEST_TIMEOUT_SEC: int = 60
