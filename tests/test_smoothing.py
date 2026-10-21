import pytest

from flappy_bird.infrastructure.tracking import OneEuroFilter, RangeMapper


def test_range_mapper_stretches_and_clamps() -> None:
    mapper = RangeMapper(0.3, 0.7)
    assert mapper(0.3) == 0.0
    assert mapper(0.5) == pytest.approx(0.5)
    assert mapper(0.7) == 1.0
    assert mapper(0.0) == 0.0
    assert mapper(1.0) == 1.0


@pytest.mark.parametrize(("top", "bottom"), [(0.5, 0.5), (0.7, 0.3), (-0.1, 0.5), (0.2, 1.2)])
def test_range_mapper_rejects_invalid_ranges(top: float, bottom: float) -> None:
    with pytest.raises(ValueError):
        RangeMapper(top, bottom)


def test_filter_first_value_passes_through() -> None:
    assert OneEuroFilter()(0.42, 0.0) == 0.42


def test_filter_reduces_jitter_when_still() -> None:
    smoother = OneEuroFilter(min_cutoff=1.0, beta=0.0)
    outputs = [smoother(0.5 + (0.02 if i % 2 else -0.02), i / 30) for i in range(60)]
    assert max(outputs[30:]) - min(outputs[30:]) < 0.01


def test_filter_follows_fast_motion_with_beta() -> None:
    lazy, reactive = OneEuroFilter(1.0, beta=0.0), OneEuroFilter(1.0, beta=10.0)
    for f in (lazy, reactive):
        f(0.0, 0.0)
    lazy_out = reactive_out = 0.0
    for i in range(1, 6):
        lazy_out = lazy(1.0, i / 30)
        reactive_out = reactive(1.0, i / 30)
    assert reactive_out > lazy_out


def test_filter_reset_forgets_history() -> None:
    smoother = OneEuroFilter()
    smoother(0.0, 0.0)
    smoother.reset()
    assert smoother(1.0, 0.1) == 1.0
