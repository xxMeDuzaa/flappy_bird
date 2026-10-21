"""El pájaro dibujado con formas vectoriales (sin imágenes).

Se dibuja en una superficie pequeña al doble de resolución y se reduce con
``smoothscale`` (*supersampling*): así los bordes quedan suavizados aunque las
primitivas de pygame no tengan antialiasing en figuras rellenas.
"""

from __future__ import annotations

import math

import pygame

from .bird_animation import WingAnimator

Point = tuple[float, float]

SUPERSAMPLE = 2

OUTLINE = (45, 32, 22)
BODY = (255, 208, 48)
BODY_SHADE = (240, 170, 30)
BELLY = (255, 238, 150)
WING = (255, 250, 235)
WING_SHADE = (225, 215, 200)
EYE_WHITE = (255, 255, 255)
PUPIL = (20, 20, 20)
BEAK_TOP = (255, 120, 40)
BEAK_BOTTOM = (225, 80, 35)


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
    """Pájaro animado. ``radius`` es el radio de la hitbox (= mitad del alto del cuerpo)."""

    def __init__(self, radius: float) -> None:
        self.radius = radius
        self.wings = WingAnimator()
        self._velocity_y = 0.0

    def update(self, dt: float, velocity_y: float) -> None:
        self._velocity_y = velocity_y
        self.wings.update(dt, velocity_y)

    def draw(self, target: pygame.Surface, center: Point, tilt: float = 0.0) -> None:
        image = self._render()
        if abs(tilt) > 0.5:
            image = pygame.transform.rotozoom(image, tilt, 1.0)
        target.blit(image, image.get_rect(center=(round(center[0]), round(center[1]))))

    # ------------------------------------------------------------------ dibujo

    def _render(self) -> pygame.Surface:
        k = SUPERSAMPLE
        r = self.radius * k
        width, height = round(r * 4.2), round(r * 4.2)
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
        tail = [
            (cx - 1.05 * r, cy - 0.35 * r),
            (cx - 1.55 * r, cy - 0.15 * r),
            (cx - 1.5 * r, cy + 0.3 * r),
            (cx - 1.0 * r, cy + 0.25 * r),
        ]
        self._poly(canvas, BODY_SHADE, tail, line)

    def _draw_body(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        body = pygame.Rect(0, 0, round(2.6 * r), round(2.0 * r))
        body.center = (round(cx), round(cy))
        pygame.draw.ellipse(canvas, BODY, body)
        belly = pygame.Rect(0, 0, round(1.7 * r), round(0.95 * r))
        belly.center = (round(cx + 0.15 * r), round(cy + 0.48 * r))
        pygame.draw.ellipse(canvas, BELLY, belly)
        pygame.draw.ellipse(canvas, OUTLINE, body, line)

    def _draw_eye(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        eye = (cx + 0.5 * r, cy - 0.38 * r)
        pygame.draw.circle(canvas, EYE_WHITE, eye, 0.46 * r)
        pygame.draw.circle(canvas, OUTLINE, eye, 0.46 * r, line)
        # La pupila mira hacia donde va el pájaro.
        look = max(-1.0, min(1.0, self._velocity_y / 600))
        pupil = (eye[0] + 0.17 * r, eye[1] + 0.16 * r * look)
        pygame.draw.circle(canvas, PUPIL, pupil, 0.17 * r)

    def _draw_beak(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        # Boca más abierta mientras sube con esfuerzo.
        open_amount = max(0.0, -self.wings.intent) * 0.12 * r
        top = [
            (cx + 0.65 * r, cy - 0.02 * r),
            (cx + 1.55 * r, cy + 0.12 * r),
            (cx + 1.5 * r, cy + 0.3 * r),
            (cx + 0.7 * r, cy + 0.3 * r),
        ]
        bottom = [
            (cx + 0.7 * r, cy + 0.3 * r + open_amount),
            (cx + 1.4 * r, cy + 0.34 * r + open_amount),
            (cx + 1.3 * r, cy + 0.55 * r + open_amount),
            (cx + 0.75 * r, cy + 0.58 * r + open_amount),
        ]
        self._poly(canvas, BEAK_BOTTOM, bottom, line)
        self._poly(canvas, BEAK_TOP, top, line)

    def _draw_wing(self, canvas: pygame.Surface, cx: float, cy: float, r: float, line: int) -> None:
        shoulder = (cx - 0.12 * r, cy + 0.04 * r)
        # Ala en reposo: un óvalo que sale del hombro hacia atrás.
        shape = _ellipse_points(shoulder[0] - 0.55 * r, shoulder[1], 0.62 * r, 0.32 * r)
        # Se gira en sentido inverso: ángulo positivo levanta la punta (que está atrás).
        wing = _rotate(shape, shoulder, -self.wings.angle)
        pygame.draw.polygon(canvas, WING, wing)
        # Plumas: líneas cortas en la mitad trasera del ala.
        feathers = _rotate(
            [
                (shoulder[0] - 0.75 * r, shoulder[1] - 0.12 * r),
                (shoulder[0] - 0.95 * r, shoulder[1] + 0.02 * r),
                (shoulder[0] - 0.75 * r, shoulder[1] + 0.16 * r),
            ],
            shoulder,
            -self.wings.angle,
        )
        pygame.draw.lines(canvas, WING_SHADE, False, feathers, line)
        pygame.draw.polygon(canvas, OUTLINE, wing, line)
