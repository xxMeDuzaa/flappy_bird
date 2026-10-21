"""Renderizado de texto con la tipografía pixel art propia (ver ``glyphs.py``).

El juego no carga fuentes ni imágenes: las letras se dibujan bloque a bloque.
Las superficies se cachean porque los mismos textos se dibujan en cada frame;
quien las use no debe modificarlas (hay que copiarlas antes, p. ej. para
cambiarles la transparencia).
"""

from __future__ import annotations

from functools import lru_cache

import pygame

from .glyphs import text_pixels, text_size
from .text import plain_text

Color = tuple[int, int, int]


@lru_cache(maxsize=256)
def render_text(scale: int, text: str, color: Color) -> pygame.Surface:
    """Texto en mayúsculas y sin acentos; cada píxel de la fuente mide ``scale`` px."""
    text = plain_text(text).upper()
    width, height = text_size(text)
    surface = pygame.Surface((max(1, width * scale), height * scale), pygame.SRCALPHA)
    for x, y in text_pixels(text):
        surface.fill(color, (x * scale, y * scale, scale, scale))
    return surface


@lru_cache(maxsize=32)
def render_outlined_text(
    scale: int, text: str, color: Color, outline: Color, thickness: int, depth: int
) -> pygame.Surface:
    """Texto "relleno" estilo arcade: contorno grueso y relieve hacia abajo.

    ``thickness`` es el grosor del contorno y ``depth`` cuánto baja el relieve (px).
    """
    fill = render_text(scale, text, color)
    edge = render_text(scale, text, outline)
    width = fill.get_width() + 2 * thickness
    height = fill.get_height() + 2 * thickness + depth
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    for dy in range(-thickness, thickness + depth + 1):
        for dx in range(-thickness, thickness + 1):
            surface.blit(edge, (thickness + dx, thickness + dy))
    surface.blit(fill, (thickness, thickness))
    return surface
