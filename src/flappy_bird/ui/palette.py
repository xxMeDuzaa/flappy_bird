"""Paletas del escenario y utilidades de color (sin dependencias de pygame).

Cada nivel de dificultad tiene su propia paleta: a medida que el jugador avanza,
el día cae hacia el atardecer y el escenario transiciona suavemente entre ellas.
"""

from __future__ import annotations

from dataclasses import dataclass, fields

Color = tuple[int, int, int]


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_color(a: Color, b: Color, t: float) -> Color:
    t = min(max(t, 0.0), 1.0)
    return (
        round(lerp(a[0], b[0], t)),
        round(lerp(a[1], b[1], t)),
        round(lerp(a[2], b[2], t)),
    )


@dataclass(frozen=True, slots=True)
class ScenePalette:
    sky_top: Color
    sky_horizon: Color
    sun: Color
    sun_glow: Color
    #: Altura del sol como fracción del alto de pantalla (0 = arriba).
    sun_height: float
    cloud_light: Color
    cloud_shadow: Color
    sea_far: Color
    sea_near: Color
    grass_light: Color
    grass_dark: Color
    ground: Color

    def blend(self, other: ScenePalette, t: float) -> ScenePalette:
        """Interpola campo por campo entre dos paletas (``t`` en ``[0, 1]``)."""
        t = min(max(t, 0.0), 1.0)
        values: dict[str, Color | float] = {}
        for field in fields(self):
            a = getattr(self, field.name)
            b = getattr(other, field.name)
            values[field.name] = lerp(a, b, t) if isinstance(a, float) else lerp_color(a, b, t)
        return ScenePalette(**values)  # type: ignore[arg-type]

    def distance(self, other: ScenePalette) -> float:
        """Diferencia máxima entre canales; sirve para saber si una transición terminó."""
        diff = 0.0
        for field in fields(self):
            a = getattr(self, field.name)
            b = getattr(other, field.name)
            if isinstance(a, float):
                diff = max(diff, abs(a - b) * 255)
            else:
                diff = max(diff, *(abs(x - y) for x, y in zip(a, b, strict=True)))
        return diff


DAY = ScenePalette(
    sky_top=(86, 196, 245),
    sky_horizon=(196, 238, 255),
    sun=(255, 255, 240),
    sun_glow=(255, 255, 220),
    sun_height=0.16,
    cloud_light=(255, 255, 255),
    cloud_shadow=(205, 205, 240),
    sea_far=(120, 190, 245),
    sea_near=(80, 150, 230),
    grass_light=(186, 230, 70),
    grass_dark=(120, 196, 72),
    ground=(132, 200, 80),
)

AFTERNOON = ScenePalette(
    sky_top=(78, 170, 235),
    sky_horizon=(225, 235, 215),
    sun=(255, 245, 200),
    sun_glow=(255, 235, 170),
    sun_height=0.26,
    cloud_light=(255, 250, 240),
    cloud_shadow=(215, 200, 225),
    sea_far=(125, 180, 225),
    sea_near=(80, 140, 210),
    grass_light=(180, 220, 70),
    grass_dark=(118, 182, 66),
    ground=(128, 188, 74),
)

GOLDEN_HOUR = ScenePalette(
    sky_top=(95, 140, 215),
    sky_horizon=(255, 210, 140),
    sun=(255, 225, 140),
    sun_glow=(255, 190, 90),
    sun_height=0.38,
    cloud_light=(255, 235, 205),
    cloud_shadow=(225, 170, 165),
    sea_far=(170, 170, 200),
    sea_near=(95, 120, 185),
    grass_light=(175, 200, 70),
    grass_dark=(118, 160, 62),
    ground=(126, 168, 68),
)

SUNSET = ScenePalette(
    sky_top=(85, 85, 165),
    sky_horizon=(255, 150, 95),
    sun=(255, 180, 100),
    sun_glow=(255, 120, 70),
    sun_height=0.50,
    cloud_light=(255, 195, 170),
    cloud_shadow=(190, 120, 150),
    sea_far=(185, 125, 150),
    sea_near=(90, 85, 150),
    grass_light=(150, 170, 70),
    grass_dark=(100, 130, 60),
    ground=(108, 140, 64),
)

DUSK = ScenePalette(
    sky_top=(35, 40, 95),
    sky_horizon=(190, 105, 120),
    sun=(255, 150, 110),
    sun_glow=(220, 90, 90),
    sun_height=0.60,
    cloud_light=(180, 140, 175),
    cloud_shadow=(110, 85, 135),
    sea_far=(120, 90, 135),
    sea_near=(55, 55, 110),
    grass_light=(110, 135, 70),
    grass_dark=(70, 100, 60),
    ground=(78, 108, 62),
)

LEVEL_PALETTES: tuple[ScenePalette, ...] = (DAY, AFTERNOON, GOLDEN_HOUR, SUNSET, DUSK)


def palette_for_level(level_index: int) -> ScenePalette:
    """Paleta del nivel (0 = primero). Niveles extra reutilizan la última."""
    index = min(max(level_index, 0), len(LEVEL_PALETTES) - 1)
    return LEVEL_PALETTES[index]
