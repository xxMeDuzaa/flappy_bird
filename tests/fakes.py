"""Dobles de prueba de los puertos de la aplicación."""

from __future__ import annotations


class InMemoryHighScoreRepository:
    """Doble de prueba del puerto ``HighScoreRepository``."""

    def __init__(self, initial: int = 0) -> None:
        self.value = initial
        self.saves: list[int] = []

    def load(self) -> int:
        return self.value

    def save(self, score: int) -> None:
        self.value = score
        self.saves.append(score)
