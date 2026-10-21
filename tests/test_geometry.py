from flappy_bird.domain import Circle, Rect


def test_rect_edges() -> None:
    rect = Rect(10, 20, 30, 40)
    assert rect.right == 40
    assert rect.bottom == 60


def test_circle_intersects_overlapping_rect() -> None:
    assert Circle(50, 50, 10).intersects(Rect(55, 0, 20, 100))


def test_circle_does_not_intersect_distant_rect() -> None:
    assert not Circle(0, 0, 10).intersects(Rect(20, 20, 10, 10))


def test_circle_near_corner_uses_real_distance() -> None:
    # La caja del círculo toca la esquina, pero el círculo no: un AABB daría falso positivo.
    rect = Rect(10, 10, 10, 10)
    assert not Circle(2, 2, 10).intersects(rect)
    assert Circle(4, 4, 10).intersects(rect)
