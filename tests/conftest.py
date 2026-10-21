from __future__ import annotations

import random

import pytest

from flappy_bird.config import GameConfig
from flappy_bird.domain import World


@pytest.fixture
def config() -> GameConfig:
    return GameConfig()


@pytest.fixture
def world(config: GameConfig) -> World:
    return World(config, rng=random.Random(1234))
