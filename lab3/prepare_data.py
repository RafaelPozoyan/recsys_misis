from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple


RatingTriplet = Tuple[int, int, float]


def parse_movielens_u_data(u_data_path: str) -> List[RatingTriplet]:
    """
    Что я делаю?
        Читаю файл MovieLens 100k u.data и преобразую его в список триплетов рейтингов.

    Что я принимаю на вход?
        u_data_path: Путь к файлу u.data.

    Что я возвращаю?
        Список (user_id, movie_id, rating).
    """
    ratings: List[RatingTriplet] = []

    with open(u_data_path, "r", encoding="utf-8") as file:
        for line in file:
            parts: List[str] = line.strip().split("\t")
            if len(parts) < 3:
                continue

            user_id: int = int(parts[0])
            movie_id: int = int(parts[1])
            rating: float = float(parts[2])
            ratings.append((user_id, movie_id, rating))

    return ratings


def parse_movielens_u_item(u_item_path: str) -> Dict[int, str]:
    """
    Что я делаю?
        Читаю файл MovieLens 100k u.item и строю словарь movie_id -> movie_title.

    Что я принимаю на вход?
        u_item_path: Путь к файлу u.item.

    Что я возвращаю?
        Словарь {movie_id: movie_title}.
    """
    movie_titles: Dict[int, str] = {}

    with open(u_item_path, "r", encoding="latin-1") as file:
        for line in file:
            parts: List[str] = line.strip().split("|")
            if len(parts) < 2:
                continue

            movie_id: int = int(parts[0])
            title: str = parts[1]
            movie_titles[movie_id] = title

    return movie_titles


def save_ratings_json(output_path: str, ratings: List[RatingTriplet]) -> None:
    """
    Что я делаю?
        Сохраняю рейтинги в JSON в формате, удобном для бота.

    Что я принимаю на вход?
        output_path: Куда сохранять JSON.
        ratings: Список (user_id, movie_id, rating).

    Что я возвращаю?
        Ничего (None).
    """
    payload: List[Dict[str, float | int]] = [
        {"user_id": user_id, "item_id": movie_id, "rating": rating}
        for user_id, movie_id, rating in ratings
    ]
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def save_movies_json(output_path: str, movies: Dict[int, str]) -> None:
    """
    Что я делаю?
        Сохраняю словарь movie_id -> title в JSON.

    Что я принимаю на вход?
        output_path: Куда сохранять.
        movies: Словарь {movie_id: title}.

    Что я возвращаю?
        Ничего (None).
    """
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(movies, file, ensure_ascii=False, indent=2)


def main() -> None:
    """
    Что я делаю?
        Конвертирую MovieLens 100k (u.data + u.item) в ratings.json и movies.json.

    Что я принимаю на вход?
        None (пути берутся из переменных ниже).

    Что я возвращаю?
        Ничего (None).
    """
    u_data_path: str = os.getenv("ML_U_DATA", "data/ml-100k/u.data")
    u_item_path: str = os.getenv("ML_U_ITEM", "data/ml-100k/u.item")

    ratings_out: str = os.getenv("RATINGS_OUT", "ratings.json")
    movies_out: str = os.getenv("MOVIES_OUT", "movies.json")

    ratings: List[RatingTriplet] = parse_movielens_u_data(u_data_path)
    movies: Dict[int, str] = parse_movielens_u_item(u_item_path)

    save_ratings_json(ratings_out, ratings)
    save_movies_json(movies_out, movies)


if __name__ == "__main__":
    main()
