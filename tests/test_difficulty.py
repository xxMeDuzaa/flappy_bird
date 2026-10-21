from itertools import pairwise

import pytest

from flappy_bird.config import DEFAULT_DIFFICULTY, DifficultyLevel
from flappy_bird.domain import level_for_score


@pytest.mark.parametrize(
    ("score", "expected_min_score"),
    [(0, 0), (4, 0), (5, 5), (12, 10), (19, 15), (20, 20), (999, 20)],
)
def test_level_for_score(score: int, expected_min_score: int) -> None:
    assert level_for_score(score, DEFAULT_DIFFICULTY).min_score == expected_min_score


def test_levels_do_not_need_to_be_sorted() -> None:
    levels = (DifficultyLevel(10, 100, 2, 3), DifficultyLevel(0, 200, 1, 3))
    assert level_for_score(3, levels).gap == 200
    assert level_for_score(10, levels).gap == 100


def test_difficulty_increases_monotonically() -> None:
    for easier, harder in pairwise(DEFAULT_DIFFICULTY):
        assert harder.speed > easier.speed
        assert harder.gap <= easier.gap


def test_requires_levels() -> None:
    with pytest.raises(ValueError):
        level_for_score(0, ())
