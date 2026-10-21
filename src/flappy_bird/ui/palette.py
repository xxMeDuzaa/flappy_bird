"""Paletas del escenario y del pájaro, y utilidades de color (sin dependencias de pygame).

Cada nivel de dificultad tiene su propia paleta: a medida que el jugador avanza,
el día cae hacia el atardecer y el pájaro se va "calentando" de amarillo claro a
rojo. Las transiciones entre paletas son graduales.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Generic, Protocol, Self, TypeVar

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


def _blend_fields(a: object, b: object, t: float) -> dict[str, Color | float]:
    """Interpola campo por campo dos dataclasses del mismo tipo (``t`` en ``[0, 1]``)."""
    t = min(max(t, 0.0), 1.0)
    values: dict[str, Color | float] = {}
    for field in fields(a):  # type: ignore[arg-type]
        x = getattr(a, field.name)
        y = getattr(b, field.name)
        values[field.name] = lerp(x, y, t) if isinstance(x, float) else lerp_color(x, y, t)
    return values


def _max_difference(a: object, b: object) -> float:
    """Diferencia máxima entre canales; sirve para saber si una transición terminó."""
    diff = 0.0
    for field in fields(a):  # type: ignore[arg-type]
        x = getattr(a, field.name)
        y = getattr(b, field.name)
        if isinstance(x, float):
            diff = max(diff, abs(x - y) * 255)
        else:
            diff = max(diff, *(abs(p - q) for p, q in zip(x, y, strict=True)))
    return diff


class Blendable(Protocol):
    def blend(self, other: Self, t: float) -> Self: ...


P = TypeVar("P", bound=Blendable)


def smoothstep(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


class PaletteTransition(Generic[P]):
    """Transición suave entre paletas.

    Siempre interpola desde la paleta de *origen* con un progreso acumulado. Si en
    cambio se mezclara la paleta actual con el destino un poquito en cada frame,
    al redondear los colores a enteros los pasos chicos darían cero y la
    transición quedaría trabada a mitad de camino.
    """

    def __init__(self, initial: P, duration: float) -> None:
        if duration <= 0:
            raise ValueError("duration debe ser positiva")
        self._duration = duration
        self._from = initial
        self._to = initial
        self._current = initial
        self._progress = 1.0

    @property
    def current(self) -> P:
        return self._current

    @property
    def done(self) -> bool:
        return self._progress >= 1.0

    def retarget(self, target: P) -> None:
        """Empieza a ir hacia ``target`` desde el color actual (si no es ya el destino)."""
        if target == self._to:
            return
        self._from = self._current
        self._to = target
        self._progress = 0.0

    def update(self, dt: float) -> bool:
        """Avanza la transición. Devuelve ``True`` si los colores cambiaron."""
        if self.done or dt <= 0:
            return False
        self._progress = min(1.0, self._progress + dt / self._duration)
        self._current = (
            self._to if self.done else self._from.blend(self._to, smoothstep(self._progress))
        )
        return True


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
        return ScenePalette(**_blend_fields(self, other, t))  # type: ignore[arg-type]

    def distance(self, other: ScenePalette) -> float:
        return _max_difference(self, other)


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


# --------------------------------------------------------------------- pájaro


@dataclass(frozen=True, slots=True)
class BirdPalette:
    body: Color
    body_shade: Color  # cola y sombra
    belly: Color
    wing: Color
    wing_shade: Color  # plumas del ala

    def blend(self, other: BirdPalette, t: float) -> BirdPalette:
        return BirdPalette(**_blend_fields(self, other, t))  # type: ignore[arg-type]

    def distance(self, other: BirdPalette) -> float:
        return _max_difference(self, other)


#: Nivel 1: amarillo claro con ala blanca. Nivel 5: rojo con ala naranja intensa pero
#: apagada (poco brillo), para que no compita con el cuerpo.
LEVEL_BIRD_PALETTES: tuple[BirdPalette, ...] = (
    BirdPalette(
        body=(255, 242, 150),
        body_shade=(242, 212, 96),
        belly=(255, 251, 218),
        wing=(255, 255, 255),
        wing_shade=(215, 215, 215),
    ),
    BirdPalette(
        body=(250, 192, 40),
        body_shade=(220, 152, 28),
        belly=(250, 208, 92),
        wing=(242, 210, 148),
        wing_shade=(200, 160, 96),
    ),
    BirdPalette(
        body=(244, 146, 40),
        body_shade=(208, 110, 30),
        belly=(252, 196, 125),
        wing=(242, 188, 112),
        wing_shade=(204, 146, 80),
    ),
    BirdPalette(
        body=(232, 102, 45),
        body_shade=(196, 72, 36),
        belly=(244, 150, 100),
        wing=(230, 140, 58),
        wing_shade=(186, 100, 40),
    ),
    BirdPalette(
        body=(196, 40, 38),
        body_shade=(150, 28, 30),
        belly=(218, 92, 74),
        wing=(214, 104, 32),
        wing_shade=(160, 72, 24),
    ),
)


def bird_palette_for_level(level_index: int) -> BirdPalette:
    index = min(max(level_index, 0), len(LEVEL_BIRD_PALETTES) - 1)
    return LEVEL_BIRD_PALETTES[index]
