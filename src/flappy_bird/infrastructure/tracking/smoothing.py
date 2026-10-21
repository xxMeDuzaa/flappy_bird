"""Procesamiento de la señal de la nariz: calibración de rango y filtrado de temblor."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RangeMapper:
    """Estira el rango ``[top, bottom]`` de la imagen a ``[0, 1]`` (con recorte)."""

    top: float
    bottom: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.top < self.bottom <= 1.0:
            raise ValueError("Se requiere 0 <= top < bottom <= 1")

    def __call__(self, value: float) -> float:
        mapped = (value - self.top) / (self.bottom - self.top)
        return min(max(mapped, 0.0), 1.0)


class OneEuroFilter:
    """Filtro *One Euro* (Casiez et al., CHI 2012).

    Es un pasa-bajos cuya frecuencia de corte crece con la velocidad de la señal:
    cuando la nariz está quieta elimina el temblor del detector, y cuando se
    mueve rápido casi no agrega retraso. Es el estándar para suavizar tracking
    de manos/cara en tiempo real.
    """

    def __init__(self, min_cutoff: float = 1.0, beta: float = 0.0, d_cutoff: float = 1.0) -> None:
        if min_cutoff <= 0 or d_cutoff <= 0:
            raise ValueError("Las frecuencias de corte deben ser positivas")
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.reset()

    def reset(self) -> None:
        self._x: float | None = None
        self._dx = 0.0
        self._t: float | None = None

    @staticmethod
    def _alpha(cutoff: float, dt: float) -> float:
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)

    def __call__(self, value: float, timestamp: float) -> float:
        if self._x is None or self._t is None:
            self._x, self._t = value, timestamp
            return value

        dt = timestamp - self._t
        if dt <= 0:
            return self._x
        self._t = timestamp

        derivative = (value - self._x) / dt
        a_d = self._alpha(self.d_cutoff, dt)
        self._dx = a_d * derivative + (1 - a_d) * self._dx

        cutoff = self.min_cutoff + self.beta * abs(self._dx)
        a = self._alpha(cutoff, dt)
        self._x = a * value + (1 - a) * self._x
        return self._x
