"""Primitivas geométricas inmutables usadas para colisiones."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Rect:
    x: float
    y: float
    width: float
    height: float

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def bottom(self) -> float:
        return self.y + self.height


@dataclass(frozen=True, slots=True)
class Circle:
    x: float
    y: float
    radius: float

    def intersects(self, rect: Rect) -> bool:
        """Colisión círculo-rectángulo: busca el punto del rectángulo más cercano al centro."""
        closest_x = min(max(self.x, rect.x), rect.right)
        closest_y = min(max(self.y, rect.y), rect.bottom)
        dx = self.x - closest_x
        dy = self.y - closest_y
        return dx * dx + dy * dy < self.radius * self.radius
