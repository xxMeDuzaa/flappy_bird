import math
from itertools import pairwise

from flappy_bird.ui.bird_animation import CLIMB, CRUISE, GLIDE, WingAnimator

DT = 1 / 60


def angles(animator: WingAnimator, velocity_y: float, seconds: float) -> list[float]:
    return [animator.update(DT, velocity_y) for _ in range(round(seconds / DT))]


def count_flaps(values: list[float]) -> int:
    """Cuenta los cruces ascendentes por la media (un aleteo completo cada uno)."""
    mean = sum(values) / len(values)
    return sum(1 for a, b in pairwise(values) if a < mean <= b)


def test_intent_follows_direction() -> None:
    climbing, diving = WingAnimator(), WingAnimator()
    angles(climbing, -1000, 1.0)
    angles(diving, 1000, 1.0)
    assert math.isclose(climbing.intent, -1.0, abs_tol=1e-3)
    assert math.isclose(diving.intent, 1.0, abs_tol=1e-3)


def test_climbing_flaps_faster_than_cruising() -> None:
    climb = angles(WingAnimator(), -1000, 3.0)[60:]
    cruise = angles(WingAnimator(), 0, 3.0)[60:]
    assert count_flaps(climb) > count_flaps(cruise)
    assert max(climb) - min(climb) > max(cruise) - min(cruise)


def test_gliding_holds_wings_up() -> None:
    glide = angles(WingAnimator(), 1000, 2.0)[60:]
    assert min(glide) > CRUISE.offset
    assert all(abs(a - GLIDE.offset) <= GLIDE.amplitude + 1e-6 for a in glide)


def test_angle_stays_within_style_bounds() -> None:
    limit = max(abs(s.offset) + s.amplitude for s in (CRUISE, CLIMB, GLIDE))
    animator = WingAnimator()
    for velocity in (-800, 0, 800, -300, 300):
        assert all(abs(a) <= limit for a in angles(animator, velocity, 0.5))


def test_direction_change_is_smooth() -> None:
    """Pasar de subir a caer no cambia el modo de golpe: se interpola en varios frames."""
    animator = WingAnimator()
    angles(animator, -1000, 1.0)
    previous = animator.intent
    biggest_step = 0.0
    for _ in range(60):
        animator.update(DT, 1000)
        biggest_step = max(biggest_step, abs(animator.intent - previous))
        previous = animator.intent
    assert biggest_step < 0.3


def test_zero_dt_does_not_change_angle() -> None:
    animator = WingAnimator()
    angles(animator, 0, 0.3)
    before = animator.angle
    assert animator.update(0, 500) == before
