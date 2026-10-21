"""Interfaces (puertos) que la capa de infraestructura debe implementar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ControlReading:
    """Una lectura del control del jugador.

    ``position`` está normalizada: 0.0 = arriba de la pantalla, 1.0 = abajo.
    ``None`` significa que no hay señal (por ejemplo, no se detecta el rostro).
    """

    position: float | None


NO_SIGNAL = ControlReading(position=None)


class ControlSource(Protocol):
    """Fuente de la posición vertical deseada por el jugador."""

    @property
    def name(self) -> str: ...

    def start(self) -> None: ...

    def read(self) -> ControlReading: ...

    def close(self) -> None: ...


@dataclass(frozen=True, slots=True)
class PreviewFrame:
    """Imagen RGB pequeña para mostrar lo que ve la cámara dentro del juego."""

    width: int
    height: int
    rgb: bytes
    #: Posición del punto seguido (nariz) en coordenadas normalizadas de la imagen.
    marker: tuple[float, float] | None


class PreviewSource(Protocol):
    def latest_preview(self) -> PreviewFrame | None: ...


class HighScoreRepository(Protocol):
    def load(self) -> int: ...

    def save(self, score: int) -> None: ...
