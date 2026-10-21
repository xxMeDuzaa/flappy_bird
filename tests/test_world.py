from __future__ import annotations

from itertools import pairwise

from flappy_bird.config import GameConfig
from flappy_bird.domain import Pipe, World

DT = 1 / 60


def gap_center(pipe: Pipe) -> float:
    return pipe.gap_top + pipe.gap_size / 2


def run_following_gaps(world: World, seconds: float) -> None:
    """Simula un jugador perfecto que siempre apunta al centro del próximo hueco."""
    for _ in range(round(seconds / DT)):
        upcoming = [p for p in world.pipes if p.right + world.bird.radius > world.bird.x]
        target = gap_center(upcoming[0]) if upcoming else None
        world.update(DT, target)


def test_first_pipe_spawns_at_right_edge(world: World) -> None:
    world.update(DT, None)
    assert len(world.pipes) == 1
    assert world.pipes[0].x <= world.width


def test_pipes_keep_constant_spacing(world: World, config: GameConfig) -> None:
    for _ in range(200):
        world.update(DT, world.height / 2)
        if world.crashed:
            break
    xs = [p.x for p in world.pipes]
    spacing = config.difficulty[0].spacing
    for a, b in pairwise(xs):
        assert abs((b - a) - spacing) < 1e-6


def test_gaps_stay_inside_screen_margins(world: World, config: GameConfig) -> None:
    run_following_gaps(world, 30)
    margin = config.pipes.edge_margin
    for pipe in world.pipes:
        assert pipe.gap_top >= margin - 1e-9
        assert pipe.gap_bottom <= world.height - margin + 1e-9


def test_perfect_player_scores_and_survives(world: World) -> None:
    run_following_gaps(world, 20)
    assert not world.crashed
    assert world.score > 5


def test_each_pipe_scores_only_once(world: World) -> None:
    run_following_gaps(world, 10)
    assert all(p.scored for p in world.pipes if p.is_passed_by(world.bird.x))


def test_idle_player_eventually_crashes(world: World) -> None:
    for _ in range(60 * 60):
        world.update(DT, 0)  # pegado al techo
        if world.crashed:
            break
    assert world.crashed


def test_crashed_world_does_not_advance(world: World) -> None:
    world.crashed = True
    world.update(DT, None)
    assert world.pipes == []


def test_score_counts_each_passed_pipe(world: World) -> None:
    passed: list[Pipe] = []  # se guardan los objetos (no ids) para que no se reutilicen
    for _ in range(60 * 15):
        upcoming = [p for p in world.pipes if p.right + world.bird.radius > world.bird.x]
        world.update(DT, gap_center(upcoming[0]) if upcoming else None)
        passed += [p for p in world.pipes if p.scored and all(p is not q for q in passed)]
    assert world.score == len(passed) > 0


def test_speed_increases_with_score(world: World, config: GameConfig) -> None:
    world.score = 20
    assert world.difficulty.speed == config.difficulty[-1].speed
