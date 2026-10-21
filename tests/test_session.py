from __future__ import annotations

import random

from flappy_bird.application import ControlReading, GameSession, GameState, ScoreBoard
from flappy_bird.application.ports import NO_SIGNAL
from flappy_bird.config import GameConfig
from flappy_bird.domain import World

from .fakes import InMemoryHighScoreRepository

DT = 1 / 60
CENTER = ControlReading(position=0.5)


def snapshot(world: World) -> tuple[float, list[float]]:
    """Estado observable del mundo: si no cambia, el mundo no avanzó."""
    return world.bird.y, [p.x for p in world.pipes]


def make_session(
    config: GameConfig, best: int = 0
) -> tuple[GameSession, InMemoryHighScoreRepository]:
    repo = InMemoryHighScoreRepository(best)
    session = GameSession(config, ScoreBoard(repo), lambda: World(config, rng=random.Random(7)))
    return session, repo


def test_starts_in_menu_and_ignores_ticks(config: GameConfig) -> None:
    session, _ = make_session(config)
    session.tick(1.0, CENTER)
    assert session.state is GameState.MENU
    assert session.world.pipes == []


def test_start_begins_playing(config: GameConfig) -> None:
    session, _ = make_session(config)
    session.start()
    session.tick(DT, CENTER)
    assert session.state is GameState.PLAYING
    assert session.world.pipes


def test_pause_freezes_world(config: GameConfig) -> None:
    session, _ = make_session(config)
    session.start()
    session.toggle_pause()
    session.tick(1.0, CENTER)
    assert session.state is GameState.PAUSED
    assert session.world.pipes == []
    session.toggle_pause()
    assert session.state is GameState.PLAYING


def test_losing_the_face_freezes_after_grace_period(config: GameConfig) -> None:
    session, _ = make_session(config)
    session.start()
    session.tick(config.face_lost_grace / 2, NO_SIGNAL)
    assert not session.waiting_for_player
    assert session.world.pipes  # durante el margen de gracia el mundo sigue
    frozen = snapshot(session.world)

    session.tick(config.face_lost_grace, NO_SIGNAL)
    assert session.waiting_for_player
    session.tick(1.0, NO_SIGNAL)
    assert snapshot(session.world) == frozen

    session.tick(DT, CENTER)
    assert not session.waiting_for_player


def test_position_is_mapped_to_screen(config: GameConfig) -> None:
    session, _ = make_session(config)
    session.start()
    radius, height = config.bird.radius, config.screen.height
    for position, expected_y in ((0.0, radius), (1.0, height - radius)):
        for _ in range(30):  # medio segundo: alcanza para llegar, antes del primer tubo
            session.tick(DT, ControlReading(position=position))
        assert abs(session.world.bird.y - expected_y) < 1


def crash(session: GameSession) -> None:
    for _ in range(60 * 60):
        session.tick(DT, ControlReading(position=0.0))
        if session.state is GameState.GAME_OVER:
            return
    raise AssertionError("la partida nunca terminó")


def test_crash_ends_game_and_saves_record_once(config: GameConfig) -> None:
    session, repo = make_session(config, best=0)
    session.start()
    session.world.score = 3
    crash(session)
    assert session.state is GameState.GAME_OVER
    assert session.new_record
    assert repo.saves == [session.world.score]


def test_no_record_when_score_is_lower(config: GameConfig) -> None:
    session, repo = make_session(config, best=1000)
    session.start()
    crash(session)
    assert not session.new_record
    assert repo.saves == []
    assert session.best_score == 1000


def test_restart_from_game_over_creates_new_world(config: GameConfig) -> None:
    session, _ = make_session(config)
    session.start()
    crash(session)
    old_world = session.world
    session.start()
    assert session.state is GameState.PLAYING
    assert session.world is not old_world
    assert session.world.score == 0


def test_start_is_ignored_while_playing(config: GameConfig) -> None:
    session, _ = make_session(config)
    session.start()
    world = session.world
    session.start()
    assert session.world is world
