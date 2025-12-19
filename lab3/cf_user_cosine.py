from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, List, Tuple

RatingTriplet = Tuple[int, int, float]  # (user_id, item_id, rating)


def calculate_cosine_similarity(
    ratings_vector_a: Dict[int, float],
    ratings_vector_b: Dict[int, float],
) -> float:
    """
    Что я делаю?
        Считаю косинусное сходство между двумя векторами оценок (User-Based CF).

    Что я принимаю на вход?
        ratings_vector_a: Вектор оценок A в виде {item_id: rating}.
        ratings_vector_b: Вектор оценок B в виде {item_id: rating}.

    Что я возвращаю?
        Значение косинусного сходства в диапазоне [0..1] (в этом контексте).
    """
    common_item_ids: set[int] = set(ratings_vector_a.keys()) & set(
        ratings_vector_b.keys()
    )
    if not common_item_ids:
        return 0.0

    dot_product: float = sum(
        ratings_vector_a[item_id] * ratings_vector_b[item_id]
        for item_id in common_item_ids
    )

    norm_a: float = math.sqrt(sum(value * value for value in ratings_vector_a.values()))
    norm_b: float = math.sqrt(sum(value * value for value in ratings_vector_b.values()))

    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0

    return dot_product / (norm_a * norm_b)


@dataclass(frozen=True)
class Recommendation:
    """
    Что я делаю?
        Храню одну рекомендацию: какой item_id рекомендовать и с каким score.

    Что я принимаю на вход?
        item_id: ID объекта.
        score: Предсказанная оценка/скор.

    Что я возвращаю?
        Экземпляр Recommendation.
    """

    item_id: int
    score: float


class UserBasedCosineCF:
    """
    User-Based Collaborative Filtering с косинусным сходством.
    """

    def __init__(self, ratings: List[RatingTriplet]) -> None:
        """
        Что я делаю?
            Строю структуру user->(item->rating) из входных триплетов.

        Что я принимаю на вход?
            ratings: Список (user_id, item_id, rating).

        Что я возвращаю?
            Ничего (None).
        """
        self.user_item_ratings: Dict[int, Dict[int, float]] = {}
        for user_id, item_id, rating in ratings:
            if user_id not in self.user_item_ratings:
                self.user_item_ratings[user_id] = {}
            self.user_item_ratings[user_id][item_id] = float(rating)

    def _get_user_vector(self, user_id: int) -> Dict[int, float]:
        """
        Что я делаю?
            Возвращаю вектор оценок пользователя.

        Что я принимаю на вход?
            user_id: ID пользователя.

        Что я возвращаю?
            Словарь {item_id: rating}.
        """
        return self.user_item_ratings.get(user_id, {})

    def find_similar_users(
        self, target_user_id: int, top_k: int
    ) -> List[Tuple[int, float]]:
        """
        Что я делаю?
            Ищу top_k самых похожих пользователей на target_user_id по cosine similarity.

        Что я принимаю на вход?
            target_user_id: ID пользователя, для которого ищем соседей.
            top_k: Сколько соседей вернуть.

        Что я возвращаю?
            Список (user_id, similarity) по убыванию similarity.
        """
        target_vector: Dict[int, float] = self._get_user_vector(target_user_id)
        if not target_vector:
            return []

        similarities: List[Tuple[int, float]] = []
        for other_user_id in self.user_item_ratings.keys():
            if other_user_id == target_user_id:
                continue
            other_vector: Dict[int, float] = self._get_user_vector(other_user_id)
            similarity: float = calculate_cosine_similarity(target_vector, other_vector)
            similarities.append((other_user_id, similarity))

        similarities.sort(key=lambda pair: pair[1], reverse=True)
        return similarities[:top_k]

    def recommend_items(
        self,
        target_user_id: int,
        neighbors_k: int = 10,
        recommendations_k: int = 5,
        min_similarity: float = 1e-9,
    ) -> List[Recommendation]:
        """
        Что я делаю?
            Рекомендую пользователю items, которые он не оценивал, на основе оценок похожих пользователей.

        Что я принимаю на вход?
            target_user_id: ID пользователя.
            neighbors_k: Сколько похожих пользователей учитывать.
            recommendations_k: Сколько рекомендаций вернуть.
            min_similarity: Порог, ниже которого сосед отбрасывается.

        Что я возвращаю?
            Список Recommendation (item_id, score), отсортированный по score.
        """
        target_vector: Dict[int, float] = self._get_user_vector(target_user_id)
        if not target_vector:
            return []

        neighbors: List[Tuple[int, float]] = self.find_similar_users(
            target_user_id, top_k=neighbors_k
        )

        rated_item_ids: set[int] = set(target_vector.keys())
        weighted_sum_by_item: Dict[int, float] = {}
        weight_sum_by_item: Dict[int, float] = {}

        for neighbor_user_id, similarity in neighbors:
            if similarity <= min_similarity:
                continue

            neighbor_vector: Dict[int, float] = self._get_user_vector(neighbor_user_id)
            for item_id, neighbor_rating in neighbor_vector.items():
                if item_id in rated_item_ids:
                    continue

                weighted_sum_by_item[item_id] = (
                    weighted_sum_by_item.get(item_id, 0.0)
                    + neighbor_rating * similarity
                )
                weight_sum_by_item[item_id] = (
                    weight_sum_by_item.get(item_id, 0.0) + similarity
                )

        recommendations: List[Recommendation] = []
        for item_id, weighted_sum in weighted_sum_by_item.items():
            weight_sum: float = weight_sum_by_item.get(item_id, 0.0)
            if weight_sum > 0.0:
                score: float = weighted_sum / weight_sum
                recommendations.append(Recommendation(item_id=item_id, score=score))

        recommendations.sort(key=lambda rec: rec.score, reverse=True)
        return recommendations[:recommendations_k]
