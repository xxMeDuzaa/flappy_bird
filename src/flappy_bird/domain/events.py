"""Eventos que emite el mundo en cada actualización."""

from enum import Enum, auto


class WorldEvent(Enum):
    SCORED = auto()
    CRASHED = auto()
