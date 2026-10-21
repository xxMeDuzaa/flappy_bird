"""Paleta de colores del juego."""

from typing import Final

Color = tuple[int, int, int]

SKY: Final[Color] = (135, 206, 235)
WHITE: Final[Color] = (255, 255, 255)
BLACK: Final[Color] = (0, 0, 0)
YELLOW: Final[Color] = (255, 221, 51)
YELLOW_SHADOW: Final[Color] = (110, 90, 0)
ORANGE: Final[Color] = (255, 140, 0)
RED: Final[Color] = (235, 64, 52)
VIOLET: Final[Color] = (138, 43, 226)
MUTED: Final[Color] = (200, 200, 200)

PIPE_BODY: Final[Color] = (60, 120, 60)
PIPE_RIM: Final[Color] = (50, 100, 50)
PIPE_BORDER: Final[Color] = (35, 80, 35)
PIPE_HIGHLIGHT: Final[Color] = (95, 160, 95)

PANEL_ALPHA: Final[int] = 160
