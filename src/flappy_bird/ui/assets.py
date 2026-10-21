"""Recursos de la interfaz: fuentes con cache.

El pájaro y el escenario se dibujan con código (ver ``bird_sprite.py`` y
``background.py``), así que el juego no carga imágenes.
"""

from __future__ import annotations

from functools import lru_cache

import pygame


@lru_cache(maxsize=16)
def font(size: int) -> pygame.font.Font:
    """Fuentes cacheadas: crearlas en cada frame es caro."""
    return pygame.font.Font(None, size)
