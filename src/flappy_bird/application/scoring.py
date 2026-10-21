"""Gestión del récord histórico."""

from __future__ import annotations

from .ports import HighScoreRepository


class ScoreBoard:
    def __init__(self, repository: HighScoreRepository) -> None:
        self._repository = repository
        self._best = max(0, repository.load())

    @property
    def best(self) -> int:
        return self._best

    def submit(self, score: int) -> bool:
        """Registra el puntaje final de una partida. Devuelve ``True`` si es un nuevo récord.

        Se persiste una sola vez al terminar la partida (no en cada punto).
        """
        if score <= self._best:
            return False
        self._best = score
        self._repository.save(score)
        return True
