"""Capa de dominio: reglas del juego puras.

No depende de pygame, OpenCV ni de ningún detalle de entrada/salida, por lo que
se puede testear de forma aislada y reutilizar con cualquier interfaz.
"""

from .bird import Bird
from .difficulty import level_for_score
from .geometry import Circle, Rect
from .pipe import Pipe
from .world import World

__all__ = ["Bird", "Circle", "Pipe", "Rect", "World", "level_for_score"]
