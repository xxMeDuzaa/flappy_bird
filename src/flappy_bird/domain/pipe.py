"""Un par de tubos (superior e inferior) separados por un hueco."""

from __future__ import annotations

from dataclasses import dataclass

from .geometry import Circle, Rect


@dataclass(slots=True)
class Pipe:
    x: float
    gap_top: float
    gap_size: float
    width: float
    screen_height: float
    scored: bool = False

    @property
    def gap_bottom(self) -> float:
        return self.gap_top + self.gap_size

    @property
    def right(self) -> float:
        return self.x + self.width

    @property
    def top_rect(self) -> Rect:
        return Rect(self.x, 0.0, self.width, self.gap_top)

    @property
    def bottom_rect(self) -> Rect:
        return Rect(self.x, self.gap_bottom, self.width, self.screen_height - self.gap_bottom)

    def move(self, dx: float) -> None:
        self.x += dx

    def collides_with(self, hitbox: Circle) -> bool:
        return hitbox.intersects(self.top_rect) or hitbox.intersects(self.bottom_rect)

    def is_passed_by(self, x: float) -> bool:
        return x > self.right

    def is_off_screen(self) -> bool:
        return self.right < 0
