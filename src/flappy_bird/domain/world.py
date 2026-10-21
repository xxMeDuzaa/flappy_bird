"""El mundo del juego: pájaro, tubos, puntaje y reglas de colisión."""

from __future__ import annotations

import random

from flappy_bird.config import DifficultyLevel, GameConfig

from .bird import Bird
from .difficulty import level_for_score
from .events import WorldEvent
from .pipe import Pipe


class World:
    """Estado de una partida. Se avanza llamando a :meth:`update` con el tiempo transcurrido."""

    def __init__(self, config: GameConfig, rng: random.Random | None = None) -> None:
        self._config = config
        self._rng = rng or random.Random()
        screen = config.screen
        bird_cfg = config.bird
        self.width = float(screen.width)
        self.height = float(screen.height)
        self.bird = Bird(
            x=self.width * bird_cfg.x_ratio,
            y=self.height / 2,
            radius=bird_cfg.radius,
            response_time=bird_cfg.response_time,
            min_y=bird_cfg.radius,
            max_y=self.height - bird_cfg.radius,
        )
        self.pipes: list[Pipe] = []
        self.score = 0
        self.crashed = False
        self.elapsed = 0.0

    @property
    def difficulty(self) -> DifficultyLevel:
        return level_for_score(self.score, self._config.difficulty)

    def update(self, dt: float, target_y: float | None) -> list[WorldEvent]:
        """Avanza la simulación ``dt`` segundos.

        ``target_y`` es la altura (px) a la que el jugador quiere llevar al pájaro;
        ``None`` mantiene el último objetivo conocido.
        """
        if self.crashed or dt <= 0:
            return []

        self.elapsed += dt
        if target_y is not None:
            self.bird.steer_to(target_y)
        self.bird.update(dt)

        level = self.difficulty
        self._spawn_pipes(level)
        for pipe in self.pipes:
            pipe.move(-level.speed * dt)

        events: list[WorldEvent] = []
        for pipe in self.pipes:
            if not pipe.scored and pipe.is_passed_by(self.bird.x):
                pipe.scored = True
                self.score += 1
                events.append(WorldEvent.SCORED)

        self.pipes = [pipe for pipe in self.pipes if not pipe.is_off_screen()]

        hitbox = self.bird.hitbox
        if any(pipe.collides_with(hitbox) for pipe in self.pipes):
            self.crashed = True
            events.append(WorldEvent.CRASHED)
        return events

    # ------------------------------------------------------------------ internos

    def _spawn_pipes(self, level: DifficultyLevel) -> None:
        if self.pipes and self.pipes[-1].x > self.width - level.spacing:
            return
        x = self.pipes[-1].x + level.spacing if self.pipes else self.width
        self.pipes.append(self._create_pipe(x, level.gap))

    def _create_pipe(self, x: float, gap: float) -> Pipe:
        cfg = self._config.pipes
        low = cfg.edge_margin
        high = self.height - cfg.edge_margin - gap
        if self.pipes:
            previous = self.pipes[-1].gap_top
            low = max(low, previous - cfg.max_gap_shift)
            high = min(high, previous + cfg.max_gap_shift)
        gap_top = self._rng.uniform(low, high) if high > low else low
        return Pipe(
            x=x,
            gap_top=gap_top,
            gap_size=gap,
            width=cfg.width,
            screen_height=self.height,
        )
