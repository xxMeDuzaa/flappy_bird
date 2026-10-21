"""El pájaro, dibujado por código en estilo pixel art (sin imágenes).

Las formas (cuerpo, ala, ojo, pico) se dibujan en una grilla chica, con bordes
duros (sin suavizado) y contorno grueso, y después se agrandan con vecino
más cercano: cada píxel del sprite se ve como un bloque cuadrado de 2x2 (juego) o
3x3 (menú) en pantalla, como en las consolas clásicas.

Los colores del cuerpo y del ala dependen del nivel (ver ``palette.py``) y
cambian gradualmente cuando sube la dificultad.
"""

from __future__ import annotations

import math

import pygame

from .bird_animation import WingAnimator
from .palette import BirdPalette, PaletteTransition, bird_palette_for_level

Point = tuple[float, float]

#: Un "píxel" del sprite cada tantos px de radio (mínimo ``MIN_PIXEL_SIZE``): el
#: pájaro grande del menú usa bloques más grandes, así ambos se ven igual de retro.
RADIUS_PER_PIXEL = 8
MIN_PIXEL_SIZE = 3
#: La inclinación va de a pasos: los sprites retro giraban "por cuadros".
TILT_STEP_DEGREES = 7.5
#: Grosor del contorno, en píxeles del sprite (con bloques grandes, 1 ya se ve marcado).
OUTLINE_PIXELS = 1
#: Duración (s) del cambio de color entre niveles.
COLOR_TRANSITION_TIME = 1.5

# Colores fijos (no cambian con el nivel).
OUTLINE = (45, 32, 22)
EYE_WHITE = (255, 255, 255)
PUPIL = (20, 20, 20)
BEAK_TOP = (255, 120, 40)
BEAK_BOTTOM = (225, 80, 35)

# Proporciones del cuerpo, en múltiplos del radio de la hitbox.
BODY_WIDTH = 2.7
BODY_HEIGHT = 2.3  # entre ovalado y redondo


def _ellipse_points(cx: float, cy: float, rx: float, ry: float, n: int = 20) -> list[Point]:
    return [
        (cx + rx * math.cos(math.tau * i / n), cy + ry * math.sin(math.tau * i / n))
        for i in range(n)
    ]


def _rotate(points: list[Point], pivot: Point, degrees: float) -> list[Point]:
    """Rota puntos alrededor de ``pivot``. Ángulos positivos giran hacia arriba en pantalla."""
    rad = math.radians(degrees)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    px, py = pivot
    return [
        (px + (x - px) * cos_a + (y - py) * sin_a, py - (x - px) * sin_a + (y - py) * cos_a)
        for x, y in points
    ]


class BirdSprite:
    """Pájaro animado. ``radius`` es el radio de la hitbox."""

    def __init__(self, radius: float) -> None:
        self.radius = radius
        self._pixel_size = max(MIN_PIXEL_SIZE, round(radius / RADIUS_PER_PIXEL))
        self.wings = WingAnimator()
        self._velocity_y = 0.0
        self._transition = PaletteTransition(bird_palette_for_level(0), COLOR_TRANSITION_TIME)

    @property
    def colors(self) -> BirdPalette:
        return self._transition.current

    def set_level(self, level_index: int) -> None:
        """Fija los colores objetivo del nivel; el cambio se hace gradual en :meth:`update`."""
        self._transition.retarget(bird_palette_for_level(level_index))

    def update(self, dt: float, velocity_y: float) -> None:
        self._velocity_y = velocity_y
        self.wings.update(dt, velocity_y)
        self._transition.update(dt)

    def draw(self, target: pygame.Surface, center: Point, tilt: float = 0.0) -> None:
        sprite = self._render()
        step = round(tilt / TILT_STEP_DEGREES) * TILT_STEP_DEGREES
        if step:
            # Se rota la grilla chica, sin suavizado, para que el borde siga pixelado.
            sprite = pygame.transform.rotate(sprite, step)
        p = self._pixel_size
        image = pygame.transform.scale(sprite, (sprite.get_width() * p, sprite.get_height() * p))
        target.blit(image, image.get_rect(center=(round(center[0]), round(center[1]))))

    # ------------------------------------------------------------------ dibujo

    def _render(self) -> pygame.Surface:
        r = self.radius / self._pixel_size  # radio en píxeles del sprite
        width, height = round(r * 5.2), round(r * 4.4)
        canvas = pygame.Surface((width, height), pygame.SRCALPHA)
        cx, cy = width / 2, height / 2
        line = OUTLINE_PIXELS
        self._draw_body(canvas, cx, cy, r, line)
        self._draw_eye(canvas, cx, cy, r, line)
        self._draw_beak(canvas, cx, cy, r, line)
        self._draw_wing(canvas, cx, cy, r, line)
        return canvas

    @staticmethod
    def _poly(
        canvas: pygame.Surface, color: tuple[int, int, int], points: list[Point], line: int
    ) -> None:
        pygame.draw.polygon(canvas, color, points)
        pygame.draw.polygon(canvas, OUTLINE, points, line)

    def _draw_body(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        body = pygame.Rect(0, 0, round(BODY_WIDTH * r), round(BODY_HEIGHT * r))
        body.center = (round(cx), round(cy))
        pygame.draw.ellipse(canvas, self.colors.body, body)
        belly = pygame.Rect(0, 0, round(1.8 * r), round(0.85 * r))
        belly.center = (round(cx + 0.2 * r), round(cy + 0.62 * r))
        pygame.draw.ellipse(canvas, self.colors.belly, belly)
        pygame.draw.ellipse(canvas, OUTLINE, body, line)

    def _draw_eye(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        eye = (cx + 0.6 * r, cy - 0.42 * r)
        pygame.draw.circle(canvas, EYE_WHITE, eye, 0.45 * r)
        pygame.draw.circle(canvas, OUTLINE, eye, 0.45 * r, line)
        # La pupila mira hacia donde va el pájaro.
        look = max(-1.0, min(1.0, self._velocity_y / 600))
        pupil = (eye[0] + 0.2 * r, eye[1] + 0.18 * r * look)
        pygame.draw.circle(canvas, PUPIL, pupil, max(1.0, 0.15 * r))

    def _draw_beak(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        # Boca más abierta mientras sube con esfuerzo.
        gap = max(0.0, -self.wings.intent) * 0.12 * r
        top = [
            (cx + 0.8 * r, cy - 0.14 * r),
            (cx + 1.85 * r, cy + 0.04 * r),
            (cx + 1.8 * r, cy + 0.36 * r),
            (cx + 0.85 * r, cy + 0.36 * r),
        ]
        bottom = [
            (cx + 0.85 * r, cy + 0.36 * r + gap),
            (cx + 1.7 * r, cy + 0.4 * r + gap),
            (cx + 1.6 * r, cy + 0.72 * r + gap),
            (cx + 0.9 * r, cy + 0.74 * r + gap),
        ]
        self._poly(canvas, BEAK_BOTTOM, bottom, line)
        self._poly(canvas, BEAK_TOP, top, line)

    def _draw_wing(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        shoulder = (cx - 0.05 * r, cy + 0.12 * r)
        # Ala grande en reposo: un óvalo que sale del hombro hacia atrás.
        shape = _ellipse_points(shoulder[0] - 0.6 * r, shoulder[1], 1.0 * r, 0.52 * r)
        # Se gira en sentido inverso: ángulo positivo levanta la punta (que está atrás).
        wing = _rotate(shape, shoulder, -self.wings.angle)
        pygame.draw.polygon(canvas, self.colors.wing, wing)
        pygame.draw.polygon(canvas, OUTLINE, wing, line)
