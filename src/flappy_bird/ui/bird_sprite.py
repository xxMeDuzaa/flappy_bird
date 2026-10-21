"""El pájaro dibujado con formas vectoriales (sin imágenes).

Se dibuja en una superficie pequeña al doble de resolución y se reduce con
``smoothscale`` (*supersampling*): así los bordes quedan suavizados aunque las
primitivas de pygame no tengan antialiasing en figuras rellenas.

Los colores del cuerpo y del ala dependen del nivel (ver ``palette.py``) y
cambian gradualmente cuando sube la dificultad.
"""

from __future__ import annotations

import math

import pygame

from .bird_animation import WingAnimator
from .palette import BirdPalette, bird_palette_for_level

Point = tuple[float, float]

SUPERSAMPLE = 2
#: Constante de tiempo (s) del cambio de color entre niveles.
COLOR_TRANSITION_TIME = 0.9

# Colores fijos (no cambian con el nivel).
OUTLINE = (45, 32, 22)
EYE_WHITE = (255, 255, 255)
PUPIL = (20, 20, 20)
BEAK_TOP = (255, 120, 40)
BEAK_BOTTOM = (225, 80, 35)

# Proporciones del cuerpo, en múltiplos del radio de la hitbox.
BODY_WIDTH = 2.55
BODY_HEIGHT = 2.25  # más alto que la hitbox: un pájaro gordito, colisión algo indulgente


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
        self.wings = WingAnimator()
        self._velocity_y = 0.0
        self._colors = bird_palette_for_level(0)
        self._target_colors = self._colors

    @property
    def colors(self) -> BirdPalette:
        return self._colors

    def set_level(self, level_index: int) -> None:
        """Fija los colores objetivo del nivel; el cambio se hace gradual en :meth:`update`."""
        self._target_colors = bird_palette_for_level(level_index)

    def update(self, dt: float, velocity_y: float) -> None:
        self._velocity_y = velocity_y
        self.wings.update(dt, velocity_y)
        if self._colors != self._target_colors and dt > 0:
            t = 1.0 - math.exp(-dt / COLOR_TRANSITION_TIME)
            blended = self._colors.blend(self._target_colors, t)
            done = blended.distance(self._target_colors) < 1
            self._colors = self._target_colors if done else blended

    def draw(self, target: pygame.Surface, center: Point, tilt: float = 0.0) -> None:
        image = self._render()
        if abs(tilt) > 0.5:
            image = pygame.transform.rotozoom(image, tilt, 1.0)
        target.blit(image, image.get_rect(center=(round(center[0]), round(center[1]))))

    # ------------------------------------------------------------------ dibujo

    def _render(self) -> pygame.Surface:
        k = SUPERSAMPLE
        r = self.radius * k
        width, height = round(r * 4.8), round(r * 4.2)
        canvas = pygame.Surface((width, height), pygame.SRCALPHA)
        cx, cy = width / 2, height / 2
        line = max(2, round(r * 0.09))

        self._draw_tail(canvas, cx, cy, r, line)
        self._draw_body(canvas, cx, cy, r, line)
        self._draw_eye(canvas, cx, cy, r, line)
        self._draw_beak(canvas, cx, cy, r, line)
        self._draw_wing(canvas, cx, cy, r, line)

        return pygame.transform.smoothscale(canvas, (width // k, height // k))

    @staticmethod
    def _poly(
        canvas: pygame.Surface, color: tuple[int, int, int], points: list[Point], line: int
    ) -> None:
        pygame.draw.polygon(canvas, color, points)
        pygame.draw.polygon(canvas, OUTLINE, points, line)

    def _draw_tail(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        # Cola en abanico: angosta donde se une al cuerpo y ancha en la punta, con el
        # borde final recto e inclinado. Nace dentro del cuerpo para que la unión quede
        # tapada y se vea el "cuello" angosto.
        neck_top = (cx - 1.1 * r, cy - 0.02 * r)
        neck_bottom = (cx - 1.05 * r, cy + 0.2 * r)
        end_top = (cx - 1.9 * r, cy - 0.52 * r)
        end_bottom = (cx - 2.12 * r, cy + 0.08 * r)
        self._poly(
            canvas, self._colors.body_shade, [neck_top, end_top, end_bottom, neck_bottom], line
        )

        # Plumas: líneas que salen de la mitad de la cola y llegan al borde final.
        neck_mid = ((neck_top[0] + neck_bottom[0]) / 2, (neck_top[1] + neck_bottom[1]) / 2)
        feather_line = max(1, line * 2 // 3)
        for t in (0.25, 0.5, 0.75):
            edge = (
                end_top[0] + (end_bottom[0] - end_top[0]) * t,
                end_top[1] + (end_bottom[1] - end_top[1]) * t,
            )
            start = (
                neck_mid[0] + (edge[0] - neck_mid[0]) * 0.45,
                neck_mid[1] + (edge[1] - neck_mid[1]) * 0.45,
            )
            pygame.draw.line(canvas, OUTLINE, start, edge, feather_line)

    def _draw_body(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        body = pygame.Rect(0, 0, round(BODY_WIDTH * r), round(BODY_HEIGHT * r))
        body.center = (round(cx), round(cy))
        pygame.draw.ellipse(canvas, self._colors.body, body)
        belly = pygame.Rect(0, 0, round(1.85 * r), round(1.15 * r))
        belly.center = (round(cx + 0.12 * r), round(cy + 0.5 * r))
        pygame.draw.ellipse(canvas, self._colors.belly, belly)
        pygame.draw.ellipse(canvas, OUTLINE, body, line)

    def _draw_eye(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        eye = (cx + 0.5 * r, cy - 0.45 * r)
        pygame.draw.circle(canvas, EYE_WHITE, eye, 0.46 * r)
        pygame.draw.circle(canvas, OUTLINE, eye, 0.46 * r, line)
        # La pupila mira hacia donde va el pájaro.
        look = max(-1.0, min(1.0, self._velocity_y / 600))
        pupil = (eye[0] + 0.17 * r, eye[1] + 0.16 * r * look)
        pygame.draw.circle(canvas, PUPIL, pupil, 0.17 * r)

    def _draw_beak(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        # Boca más abierta mientras sube con esfuerzo.
        gap = max(0.0, -self.wings.intent) * 0.12 * r
        top = [
            (cx + 0.7 * r, cy - 0.02 * r),
            (cx + 1.85 * r, cy + 0.14 * r),
            (cx + 1.8 * r, cy + 0.32 * r),
            (cx + 0.75 * r, cy + 0.32 * r),
        ]
        bottom = [
            (cx + 0.75 * r, cy + 0.32 * r + gap),
            (cx + 1.65 * r, cy + 0.36 * r + gap),
            (cx + 1.55 * r, cy + 0.58 * r + gap),
            (cx + 0.8 * r, cy + 0.6 * r + gap),
        ]
        self._poly(canvas, BEAK_BOTTOM, bottom, line)
        self._poly(canvas, BEAK_TOP, top, line)

    def _draw_wing(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        shoulder = (cx - 0.12 * r, cy + 0.08 * r)
        # Ala en reposo: un óvalo que sale del hombro hacia atrás.
        shape = _ellipse_points(shoulder[0] - 0.58 * r, shoulder[1], 0.66 * r, 0.34 * r)
        # Se gira en sentido inverso: ángulo positivo levanta la punta (que está atrás).
        wing = _rotate(shape, shoulder, -self.wings.angle)
        pygame.draw.polygon(canvas, self._colors.wing, wing)
        # Plumas: líneas cortas en la mitad trasera del ala.
        feathers = _rotate(
            [
                (shoulder[0] - 0.8 * r, shoulder[1] - 0.13 * r),
                (shoulder[0] - 1.0 * r, shoulder[1] + 0.02 * r),
                (shoulder[0] - 0.8 * r, shoulder[1] + 0.17 * r),
            ],
            shoulder,
            -self.wings.angle,
        )
        pygame.draw.lines(canvas, self._colors.wing_shade, False, feathers, line)
        pygame.draw.polygon(canvas, OUTLINE, wing, line)
