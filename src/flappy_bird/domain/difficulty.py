"""Selección del nivel de dificultad según el puntaje."""

from __future__ import annotations

from collections.abc import Sequence

from flappy_bird.config import DifficultyLevel


def level_for_score(score: int, levels: Sequence[DifficultyLevel]) -> DifficultyLevel:
    """Devuelve el nivel más alto cuyo ``min_score`` ya fue alcanzado."""
    if not levels:
        raise ValueError("Se necesita al menos un nivel de dificultad")
    ordered = sorted(levels, key=lambda level: level.min_score)
    current = ordered[0]
    for level in ordered:
        if score >= level.min_score:
            current = level
    return current
