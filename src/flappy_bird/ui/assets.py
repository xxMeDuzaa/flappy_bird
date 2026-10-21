"""Carga de imágenes y fuentes con cache y valores de respaldo."""

from __future__ import annotations

import logging
from functools import lru_cache
from pathlib import Path

import pygame

logger = logging.getLogger(__name__)

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
IMAGES_DIR = ASSETS_DIR / "images"


def load_image(name: str, *, alpha: bool = True) -> pygame.Surface | None:
    """Carga ``assets/images/<name>``; devuelve ``None`` (y lo registra) si falla."""
    path = IMAGES_DIR / name
    try:
        image = pygame.image.load(path)
    except (FileNotFoundError, pygame.error) as error:
        logger.warning("No se pudo cargar %s (%s); se usa un dibujo de respaldo", path, error)
        return None
    return image.convert_alpha() if alpha else image.convert()


@lru_cache(maxsize=16)
def font(size: int) -> pygame.font.Font:
    """Fuentes cacheadas: crearlas en cada frame es caro."""
    return pygame.font.Font(None, size)
