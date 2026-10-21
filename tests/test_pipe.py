from flappy_bird.domain import Circle, Pipe


def make_pipe() -> Pipe:
    return Pipe(x=200, gap_top=200, gap_size=200, width=80, screen_height=600)


def test_rects_cover_everything_except_gap() -> None:
    pipe = make_pipe()
    assert pipe.top_rect.height == 200
    assert pipe.bottom_rect.y == 400
    assert pipe.bottom_rect.bottom == 600


def test_bird_inside_gap_does_not_collide() -> None:
    assert not make_pipe().collides_with(Circle(240, 300, 20))


def test_bird_touching_top_pipe_collides() -> None:
    assert make_pipe().collides_with(Circle(240, 215, 20))


def test_bird_touching_bottom_pipe_collides() -> None:
    assert make_pipe().collides_with(Circle(240, 385, 20))


def test_passed_and_off_screen() -> None:
    pipe = make_pipe()
    assert not pipe.is_passed_by(250)
    assert pipe.is_passed_by(281)
    pipe.move(-300)
    assert pipe.is_off_screen()
