"""Contrato común para los detectores de nariz."""

from __future__ import annotations

from typing import Protocol

import numpy as np
from numpy.typing import NDArray


class TrackerUnavailableError(RuntimeError):
    """El detector no se puede usar en este equipo (falta la librería, el modelo, etc.)."""


class NoseTracker(Protocol):
    @property
    def name(self) -> str: ...

    def locate(self, frame_bgr: NDArray[np.uint8]) -> tuple[float, float] | None:
        """Devuelve la posición de la nariz normalizada ``(x, y)`` en ``[0, 1]``, o ``None``."""
        ...

    def close(self) -> None: ...
