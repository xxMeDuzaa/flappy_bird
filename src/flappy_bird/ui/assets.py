"""Recursos de la interfaz: fuentes con cache.

El pájaro y el escenario se dibujan con código (ver ``bird_sprite.py`` y
``background.py``), así que el juego no carga imágenes.
"""

from __future__ import annotations

from functools import lru_cache

import pygame

from .text import plain_text


@lru_cache(maxsize=16)
def font(size: int) -> pygame.font.Font:
    """Fuentes cacheadas: crearlas en cada frame es caro."""
    return pygame.font.Font(None, size)


def render_text(size: int, text: str, color: tuple[int, int, int]) -> pygame.Surface:
    """Renderiza texto sin acentos (la fuente por defecto los dibuja mal)."""
    return font(size).render(plain_text(text), True, color)
