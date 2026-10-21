import pytest

from flappy_bird.domain import Bird


def make_bird() -> Bird:
    return Bird(x=100, y=300, radius=20, response_time=0.1, min_y=20, max_y=580)


def test_bird_moves_towards_target() -> None:
    bird = make_bird()
    bird.steer_to(100)
    bird.update(0.05)
    assert 100 < bird.y < 300
    assert bird.velocity_y < 0


def test_bird_converges_to_target() -> None:
    bird = make_bird()
    bird.steer_to(500)
    for _ in range(120):
        bird.update(1 / 60)
    assert bird.y == pytest.approx(500, abs=0.5)


def test_movement_is_independent_of_frame_rate() -> None:
    fast, slow = make_bird(), make_bird()
    fast.steer_to(100)
    slow.steer_to(100)
    for _ in range(60):
        fast.update(1 / 60)
    for _ in range(30):
        slow.update(1 / 30)
    assert fast.y == pytest.approx(slow.y, abs=1e-6)


def test_target_is_clamped_to_screen() -> None:
    bird = make_bird()
    bird.steer_to(-1000)
    assert bird.target_y == 20
    bird.steer_to(10_000)
    assert bird.target_y == 580


def test_invalid_response_time() -> None:
    with pytest.raises(ValueError):
        Bird(x=0, y=0, radius=1, response_time=0, min_y=0, max_y=1)
