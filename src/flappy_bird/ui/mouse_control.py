"""Control alternativo con el mouse (para probar o jugar sin cámara)."""

from __future__ import annotations

import pygame

from flappy_bird.application.ports import NO_SIGNAL, ControlReading


class MouseControl:
    name = "Mouse"

    def __init__(self, screen_height: int) -> None:
        self._screen_height = screen_height

    def start(self) -> None:
        pass

    def read(self) -> ControlReading:
        if not pygame.mouse.get_focused():
            return NO_SIGNAL
        _, y = pygame.mouse.get_pos()
        return ControlReading(position=y / max(1, self._screen_height - 1))

    def close(self) -> None:
        pass
