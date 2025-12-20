from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

RatingTriplet = Tuple[int, int, float]


def load_ratings(file_path: str) -> List[RatingTriplet]:
    """
    Загружает оценки пользователей из json-файла

    Args:
        file_path: Путь к файлу

    Returns:
        Список (user_id, item_id, rating)
    """
    if not os.path.exists(file_path):
        return []

    with open(file_path, "r", encoding="utf-8") as file:
        raw_rows: List[Dict[str, object]] = json.load(file)

    ratings: List[RatingTriplet] = []
    for row in raw_rows:
        ratings.append((int(row["user_id"]), int(row["item_id"]), float(row["rating"])))

    return ratings


def save_ratings(file_path: str, ratings: List[RatingTriplet]) -> None:
    """
    Сохраняет оценки пользователей в json-файл

    Args:
        file_path: Путь к файлу
        ratings: Список (user_id, item_id, rating)
    """
    payload: List[Dict[str, object]] = [
        {"user_id": user_id, "item_id": item_id, "rating": rating}
        for user_id, item_id, rating in ratings
    ]

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def upsert_rating(
    ratings: List[RatingTriplet],
    user_id: int,
    item_id: int,
    rating: float,
) -> List[RatingTriplet]:
    """
    Добавляет новую оценку или обновляет существующую для item_id

    Args:
        ratings: Текущий список оценок
        user_id: ID пользователя
        item_id: ID объекта
        rating: Оценка

    Return:
        updated_ratings: Новый список оценок с обновлением
    """
    updated_ratings: List[RatingTriplet] = []
    was_updated: bool = False

    for existing_user_id, existing_item_id, existing_rating in ratings:
        if existing_user_id == user_id and existing_item_id == item_id:
            updated_ratings.append((user_id, item_id, rating))
            was_updated = True
        else:
            updated_ratings.append(
                (existing_user_id, existing_item_id, existing_rating)
            )

    if not was_updated:
        updated_ratings.append((user_id, item_id, rating))

    return updated_ratings
