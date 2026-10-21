"""Escenario de fondo generado por código (sin imágenes).

Se dibuja con formas vectoriales (degradés, círculos y polígonos) en varias capas
con *parallax*: cada capa se desplaza a una fracción distinta de la velocidad del
juego, lo que da sensación de profundidad.

Las superficies que dependen de la paleta (cielo, sol, nubes, mar y pasto) se
pre-renderizan y sólo se regeneran cuando cambian los colores, así cada frame
se limita a unos pocos ``blit``.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from .palette import DAY, PaletteTransition, ScenePalette, lerp_color, palette_for_level

#: Fracciones del alto de pantalla donde empiezan el mar y el pasto.
HORIZON_RATIO = 0.70
GROUND_RATIO = 0.80

#: Factor de parallax de cada capa respecto de la velocidad de los tubos.
FAR_CLOUDS_FACTOR = 0.04
NEAR_CLOUDS_FACTOR = 0.10
SEA_FACTOR = 0.20
GROUND_FACTOR = 1.0  # el pasto acompaña a los tubos

#: Viento: las nubes se mueven un poco aunque el juego esté quieto (px/s).
WIND_SPEED = 6.0
#: Duración (s) de la transición de colores entre niveles.
PALETTE_TRANSITION_TIME = 2.0

#: Durante una transición, cada cuánto (s) se regeneran las superficies. Los colores
#: cambian lento, así que 12 veces por segundo se ve fluido y cuesta mucho menos.
REBUILD_INTERVAL = 0.08

#: Período (px) del patrón del pasto; la textura se repite cada esta distancia.
GROUND_PERIOD = 96
TUFT_STEP = 8
STRIPE_STEP = 24
GRASS_BAND = 16
TUFT_HEIGHTS = (6, 10, 7, 12, 8, 5, 11, 7, 9, 6, 12, 8)  # 12 * 8 px = GROUND_PERIOD


@dataclass(slots=True)
class _Cloud:
    x: float
    y: float
    factor: float
    #: Círculos que forman la nube: (dx, dy, radio) relativos a su esquina.
    puffs: list[tuple[int, int, int]]
    width: int
    height: int
    surface: pygame.Surface | None = None


@dataclass(slots=True)
class _Sparkle:
    x: float
    y: float
    length: int
    phase: float


class SceneBackground:
    def __init__(self, size: tuple[int, int], rng: random.Random | None = None) -> None:
        self._width, self._height = size
        self._horizon_y = round(self._height * HORIZON_RATIO)
        self._ground_y = round(self._height * GROUND_RATIO)
        rng = rng or random.Random(2024)

        self._transition = PaletteTransition(DAY, PALETTE_TRANSITION_TIME)
        self._dirty = True
        self._scroll = 0.0
        self._time = 0.0
        self._last_rebuild = -math.inf

        self._clouds = [
            *(self._make_cloud(rng, FAR_CLOUDS_FACTOR, scale=0.6) for _ in range(6)),
            *(self._make_cloud(rng, NEAR_CLOUDS_FACTOR, scale=1.0) for _ in range(4)),
        ]
        self._clouds.sort(key=lambda cloud: cloud.factor)  # las lejanas se dibujan primero
        self._sparkles = [
            _Sparkle(
                x=rng.uniform(0, self._width),
                y=rng.uniform(self._horizon_y + 6, self._ground_y - 4),
                length=rng.randint(6, 18),
                phase=rng.uniform(0, math.tau),
            )
            for _ in range(28)
        ]

        self._sky: pygame.Surface | None = None
        self._sun: pygame.Surface | None = None
        self._sea: pygame.Surface | None = None
        self._ground: pygame.Surface | None = None

    # ---------------------------------------------------------------- control

    def set_level(self, level_index: int) -> None:
        """Cambia la paleta objetivo; la transición ocurre gradualmente en :meth:`update`."""
        self._transition.retarget(palette_for_level(level_index))

    def update(self, dt: float, speed: float) -> None:
        """Avanza las animaciones. ``speed`` es la velocidad actual de los tubos (px/s)."""
        self._time += dt
        self._scroll += speed * dt

        if self._transition.update(dt):
            self._dirty = True

    @property
    def _palette(self) -> ScenePalette:
        return self._transition.current

    def draw(self, surface: pygame.Surface) -> None:
        transition_done = self._transition.done
        if self._dirty and (transition_done or self._time - self._last_rebuild >= REBUILD_INTERVAL):
            self._rebuild()
            self._dirty = False
            self._last_rebuild = self._time
        assert self._sky is not None and self._sun is not None
        assert self._sea is not None and self._ground is not None

        surface.blit(self._sky, (0, 0))
        sun_center = (round(self._width * 0.30), round(self._height * self._palette.sun_height))
        surface.blit(self._sun, self._sun.get_rect(center=sun_center))
        self._draw_clouds(surface)
        surface.blit(self._sea, (0, self._horizon_y))
        self._draw_sparkles(surface)
        offset = -(self._scroll * GROUND_FACTOR % GROUND_PERIOD)
        surface.blit(self._ground, (round(offset), self._ground_y - max(TUFT_HEIGHTS)))

    # ------------------------------------------------------------ capas vivas

    def _draw_clouds(self, surface: pygame.Surface) -> None:
        for cloud in self._clouds:
            assert cloud.surface is not None
            span = self._width + cloud.width
            travelled = self._scroll * cloud.factor + self._time * WIND_SPEED * cloud.factor * 10
            x = (cloud.x - travelled) % span - cloud.width
            surface.blit(cloud.surface, (round(x), round(cloud.y)))

    def _draw_sparkles(self, surface: pygame.Surface) -> None:
        base = self._palette.sea_near
        for sparkle in self._sparkles:
            twinkle = 0.5 + 0.5 * math.sin(self._time * 2.2 + sparkle.phase)
            color = lerp_color(base, (255, 255, 255), 0.25 + 0.55 * twinkle)
            span = self._width + sparkle.length
            x = (sparkle.x - self._scroll * SEA_FACTOR) % span - sparkle.length
            y = round(sparkle.y)
            pygame.draw.line(surface, color, (round(x), y), (round(x) + sparkle.length, y), 2)

    # ------------------------------------------------ superficies pre-renderizadas

    def _rebuild(self) -> None:
        palette = self._palette
        self._sky = self._vertical_gradient(
            (self._width, self._horizon_y), palette.sky_top, palette.sky_horizon
        )
        self._sun = self._render_sun(palette)
        self._sea = self._render_sea(palette)
        self._ground = self._render_ground(palette)
        for cloud in self._clouds:
            cloud.surface = self._render_cloud(cloud, palette)

    @staticmethod
    def _vertical_gradient(
        size: tuple[int, int], top: tuple[int, int, int], bottom: tuple[int, int, int]
    ) -> pygame.Surface:
        width, height = size
        column = pygame.Surface((1, height))
        for y in range(height):
            column.fill(lerp_color(top, bottom, y / max(1, height - 1)), (0, y, 1, 1))
        return pygame.transform.smoothscale(column, (width, height))

    @staticmethod
    def _render_sun(palette: ScenePalette) -> pygame.Surface:
        radius, glow = 34, 110
        sun = pygame.Surface((glow * 2, glow * 2), pygame.SRCALPHA)
        rings = 10
        for i in range(rings):  # halo: anillos concéntricos cada vez más opacos
            r = glow - i * (glow - radius) // rings
            alpha = round(10 + 50 * (i / rings) ** 2)
            pygame.draw.circle(sun, (*palette.sun_glow, alpha), (glow, glow), r)
        pygame.draw.circle(sun, palette.sun, (glow, glow), radius)
        return sun

    def _render_sea(self, palette: ScenePalette) -> pygame.Surface:
        height = self._ground_y - self._horizon_y
        sea = self._vertical_gradient((self._width, height), palette.sea_far, palette.sea_near)
        shoreline = lerp_color(palette.sky_horizon, (255, 255, 255), 0.5)
        pygame.draw.line(sea, shoreline, (0, 0), (self._width, 0), 3)
        return sea

    def _render_ground(self, palette: ScenePalette) -> pygame.Surface:
        tuft_room = max(TUFT_HEIGHTS)
        width = self._width + GROUND_PERIOD
        height = self._height - self._ground_y + tuft_room
        ground = pygame.Surface((width, height), pygame.SRCALPHA)
        top = tuft_room

        ground.fill(palette.ground, (0, top, width, height - top))
        # Rayas diagonales: dan sensación de velocidad al desplazarse.
        stripe_color = lerp_color(palette.ground, palette.grass_dark, 0.6)
        for x in range(-height, width + height, STRIPE_STEP):
            stripe = [
                (x, height),
                (x + 10, height),
                (x + 10 + (height - top - GRASS_BAND), top + GRASS_BAND),
                (x + (height - top - GRASS_BAND), top + GRASS_BAND),
            ]
            pygame.draw.polygon(ground, stripe_color, stripe)

        ground.fill(palette.grass_light, (0, top, width, GRASS_BAND))
        ground.fill(palette.grass_dark, (0, top + GRASS_BAND, width, 4))
        for i, x in enumerate(range(0, width + TUFT_STEP, TUFT_STEP)):
            tuft_h = TUFT_HEIGHTS[i % len(TUFT_HEIGHTS)]
            blade = [(x, top + 2), (x + TUFT_STEP // 2, top - tuft_h), (x + TUFT_STEP, top + 2)]
            pygame.draw.polygon(ground, palette.grass_light, blade)
        return ground

    # -------------------------------------------------------------------- nubes

    def _make_cloud(self, rng: random.Random, factor: float, scale: float) -> _Cloud:
        base = round(rng.uniform(22, 32) * scale)
        count = rng.randint(4, 6)
        puffs: list[tuple[int, int, int]] = []
        x = base
        for i in range(count):
            # Bultos más grandes en el centro, más chicos en los extremos.
            middle = 1.0 - abs(i - (count - 1) / 2) / count
            radius = round(base * (0.7 + 0.6 * middle) * rng.uniform(0.9, 1.1))
            puffs.append((x, 0, radius))
            x += round(radius * rng.uniform(0.9, 1.2))
        max_r = max(r for _, _, r in puffs)
        width = x + max_r
        height = round(max_r * 2.4)  # margen arriba para el cuerpo iluminado
        # Alinea las bases de los bultos en una misma línea.
        puffs = [(px, height - r - 2, r) for px, _, r in puffs]
        y = rng.uniform(self._height * 0.10, self._horizon_y * 0.65)
        return _Cloud(
            x=rng.uniform(0, self._width + width),
            y=y,
            factor=factor,
            puffs=puffs,
            width=width,
            height=height,
        )

    @staticmethod
    def _render_cloud(cloud: _Cloud, palette: ScenePalette) -> pygame.Surface:
        surface = pygame.Surface((cloud.width, cloud.height), pygame.SRCALPHA)
        for x, y, r in cloud.puffs:  # sombra inferior
            pygame.draw.circle(surface, palette.cloud_shadow, (x, y), r)
        for x, y, r in cloud.puffs:  # cuerpo iluminado, corrido hacia arriba
            pygame.draw.circle(surface, palette.cloud_light, (x, y - r // 3), round(r * 0.82))
        # Base plana, como las nubes del Flappy Bird original, dejando ver la sombra.
        min_radius = min(r for _, _, r in cloud.puffs)
        flat_from = max(y for _, y, _ in cloud.puffs) + round(min_radius * 0.7)
        surface.fill((0, 0, 0, 0), (0, flat_from, cloud.width, cloud.height - flat_from))
        return surface
