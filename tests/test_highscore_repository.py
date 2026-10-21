from pathlib import Path

from flappy_bird.application import ScoreBoard
from flappy_bird.infrastructure.storage import JsonHighScoreRepository

from .fakes import InMemoryHighScoreRepository


def test_missing_file_returns_zero(tmp_path: Path) -> None:
    assert JsonHighScoreRepository(tmp_path / "nope.json").load() == 0


def test_round_trip_creates_parent_dirs(tmp_path: Path) -> None:
    path = tmp_path / "a" / "b" / "highscore.json"
    repo = JsonHighScoreRepository(path)
    repo.save(42)
    assert repo.load() == 42
    assert not path.with_suffix(".tmp").exists()


def test_corrupt_file_returns_zero(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"
    path.write_text("{no es json", encoding="utf-8")
    assert JsonHighScoreRepository(path).load() == 0


def test_invalid_values_return_zero(tmp_path: Path) -> None:
    path = tmp_path / "highscore.json"
    for content in ('{"high_score": -3}', '{"high_score": "10"}', "[1, 2]", '{"high_score": true}'):
        path.write_text(content, encoding="utf-8")
        assert JsonHighScoreRepository(path).load() == 0


def test_scoreboard_only_saves_improvements() -> None:
    repo = InMemoryHighScoreRepository(10)
    board = ScoreBoard(repo)
    assert board.best == 10
    assert not board.submit(5)
    assert not board.submit(10)
    assert board.submit(11)
    assert board.best == 11
    assert repo.saves == [11]
