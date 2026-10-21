"""Capa de aplicación: orquesta el dominio y define los puertos hacia el exterior.

Los *puertos* (``ports.py``) son interfaces (``Protocol``) que la infraestructura
implementa: de dónde sale la posición del jugador y dónde se guarda el récord.
La lógica de la partida no sabe si la entrada es una cámara o un mouse.
"""

from .ports import ControlReading, ControlSource, HighScoreRepository, PreviewFrame, PreviewSource
from .scoring import ScoreBoard
from .session import GameSession, GameState

__all__ = [
    "ControlReading",
    "ControlSource",
    "GameSession",
    "GameState",
    "HighScoreRepository",
    "PreviewFrame",
    "PreviewSource",
    "ScoreBoard",
]
