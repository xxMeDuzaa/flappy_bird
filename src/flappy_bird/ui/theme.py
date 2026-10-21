"""Paleta de colores del juego."""

from typing import Final

Color = tuple[int, int, int]

WHITE: Final[Color] = (255, 255, 255)
BLACK: Final[Color] = (0, 0, 0)
YELLOW: Final[Color] = (255, 221, 51)
RED: Final[Color] = (235, 64, 52)
GREEN: Final[Color] = (90, 210, 110)
MUTED: Final[Color] = (200, 200, 200)
#: Mismo contorno oscuro que el pájaro: el título comparte su estilo de dibujo.
OUTLINE: Final[Color] = (45, 32, 22)
#: Amarillo limón del pájaro en el nivel 1.
TITLE: Final[Color] = (255, 234, 92)

PIPE_BODY: Final[Color] = (60, 120, 60)
PIPE_RIM: Final[Color] = (50, 100, 50)
PIPE_BORDER: Final[Color] = (35, 80, 35)
PIPE_HIGHLIGHT: Final[Color] = (95, 160, 95)

PANEL_ALPHA: Final[int] = 160
