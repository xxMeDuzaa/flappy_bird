"""El pájaro: sigue suavemente una altura objetivo que dicta el jugador."""

from __future__ import annotations

import math

from .geometry import Circle


class Bird:
    def __init__(
        self,
        x: float,
        y: float,
        radius: float,
        response_time: float,
        min_y: float,
        max_y: float,
    ) -> None:
        if response_time <= 0:
            raise ValueError("response_time debe ser positivo")
        self.x = x
        self.y = y
        self.radius = radius
        self.response_time = response_time
        self.min_y = min_y
        self.max_y = max_y
        self.velocity_y = 0.0
        self._target_y = y

    @property
    def target_y(self) -> float:
        return self._target_y

    def steer_to(self, target_y: float) -> None:
        """Fija la altura a la que el pájaro debe dirigirse (se limita a la pantalla)."""
        self._target_y = min(max(target_y, self.min_y), self.max_y)

    def update(self, dt: float) -> None:
        """Acerca el pájaro a su objetivo con un suavizado exponencial independiente de los FPS."""
        if dt <= 0:
            return
        alpha = 1.0 - math.exp(-dt / self.response_time)
        new_y = self.y + (self._target_y - self.y) * alpha
        self.velocity_y = (new_y - self.y) / dt
        self.y = new_y

    @property
    def hitbox(self) -> Circle:
        return Circle(self.x, self.y, self.radius)
