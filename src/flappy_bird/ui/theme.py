"""Paleta de colores del juego."""

from typing import Final

Color = tuple[int, int, int]

WHITE: Final[Color] = (255, 255, 255)
BLACK: Final[Color] = (0, 0, 0)
RED: Final[Color] = (235, 64, 52)
GREEN: Final[Color] = (90, 210, 110)
MUTED: Final[Color] = (200, 200, 200)
#: Mismo contorno oscuro que el pájaro: el título comparte su estilo de dibujo.
OUTLINE: Final[Color] = (45, 32, 22)
#: Amarillo limón del pájaro en el nivel 1.
TITLE: Final[Color] = (255, 234, 92)

# Tubos: tonos más vivos, con luz y sombra, para el estilo de dibujo animado.
PIPE_BODY: Final[Color] = (96, 176, 70)
PIPE_HIGHLIGHT: Final[Color] = (152, 214, 106)
PIPE_SHADE: Final[Color] = (64, 132, 52)

PANEL_ALPHA: Final[int] = 160
