import pytest

from flappy_bird.ui.palette import DAY, DUSK, LEVEL_PALETTES, lerp_color, palette_for_level


def test_lerp_color_endpoints_and_clamp() -> None:
    assert lerp_color((0, 0, 0), (100, 200, 50), 0.0) == (0, 0, 0)
    assert lerp_color((0, 0, 0), (100, 200, 50), 0.5) == (50, 100, 25)
    assert lerp_color((0, 0, 0), (100, 200, 50), 2.0) == (100, 200, 50)


def test_blend_endpoints() -> None:
    assert DAY.blend(DUSK, 0.0) == DAY
    assert DAY.blend(DUSK, 1.0) == DUSK


def test_blend_midpoint_is_between() -> None:
    mid = DAY.blend(DUSK, 0.5)
    assert (
        min(DAY.sun_height, DUSK.sun_height) < mid.sun_height < max(DAY.sun_height, DUSK.sun_height)
    )
    assert 0 < mid.distance(DAY) < DAY.distance(DUSK)


def test_distance_is_zero_for_same_palette() -> None:
    assert DAY.distance(DAY) == 0


@pytest.mark.parametrize(("level", "expected"), [(-1, 0), (0, 0), (2, 2), (99, -1)])
def test_palette_for_level_is_clamped(level: int, expected: int) -> None:
    assert palette_for_level(level) == LEVEL_PALETTES[expected]


def test_sun_sets_as_levels_increase() -> None:
    heights = [p.sun_height for p in LEVEL_PALETTES]
    assert heights == sorted(heights)


def test_bird_palettes_get_darker_and_redder() -> None:
    from flappy_bird.ui.palette import LEVEL_BIRD_PALETTES, bird_palette_for_level

    def brightness(color: tuple[int, int, int]) -> int:
        return sum(color)

    bodies = [p.body for p in LEVEL_BIRD_PALETTES]
    assert [brightness(c) for c in bodies] == sorted((brightness(c) for c in bodies), reverse=True)
    first, last = LEVEL_BIRD_PALETTES[0], LEVEL_BIRD_PALETTES[-1]
    assert first.wing == (255, 255, 255)
    red, green, blue = last.body
    assert red > 2 * green and red > 2 * blue  # termina en rojo
    wr, wg, wb = last.wing
    assert wr > wg > wb  # ala anaranjada
    assert bird_palette_for_level(99) == last
