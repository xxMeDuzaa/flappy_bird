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
    assert mid not in (DAY, DUSK)


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


def test_transition_reaches_target_exactly() -> None:
    from flappy_bird.ui.palette import LEVEL_BIRD_PALETTES, PaletteTransition

    transition = PaletteTransition(LEVEL_BIRD_PALETTES[0], duration=1.0)
    transition.retarget(LEVEL_BIRD_PALETTES[1])
    for _ in range(120):  # 2 s a 60 FPS: pasos muy chicos en cada frame
        transition.update(1 / 60)
    assert transition.done
    assert transition.current == LEVEL_BIRD_PALETTES[1]


def test_transition_does_not_stall_on_small_steps() -> None:
    from flappy_bird.ui.palette import LEVEL_BIRD_PALETTES, PaletteTransition

    start, end = LEVEL_BIRD_PALETTES[0], LEVEL_BIRD_PALETTES[1]
    transition = PaletteTransition(start, duration=1.0)
    transition.retarget(end)
    for _ in range(45):  # 75 % del tiempo
        transition.update(1 / 60)
    # Con el bug anterior los colores se trababan cerca del origen: acá deben
    # estar más cerca del destino que del origen en cada canal que cambia.
    for field in ("body", "belly", "wing"):
        now, a, b = (getattr(x, field) for x in (transition.current, start, end))
        for channel, (c_now, c_a, c_b) in enumerate(zip(now, a, b, strict=True)):
            if c_a != c_b:
                assert abs(c_now - c_b) < abs(c_now - c_a), (field, channel)


def test_retarget_mid_transition_starts_from_current_colors() -> None:
    from flappy_bird.ui.palette import LEVEL_BIRD_PALETTES, PaletteTransition

    transition = PaletteTransition(LEVEL_BIRD_PALETTES[0], duration=1.0)
    transition.retarget(LEVEL_BIRD_PALETTES[4])
    transition.update(0.5)
    mid = transition.current
    transition.retarget(LEVEL_BIRD_PALETTES[0])
    transition.update(1e-6)
    assert all(
        abs(x - y) <= 1
        for field in ("body", "belly", "wing")
        for x, y in zip(getattr(transition.current, field), getattr(mid, field), strict=True)
    )
    assert not transition.update(0) and not transition.done
