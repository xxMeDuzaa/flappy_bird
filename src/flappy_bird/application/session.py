"""Máquina de estados de una sesión de juego (menú → jugando → pausa → game over)."""

from __future__ import annotations

from collections.abc import Callable
from enum import Enum, auto

from flappy_bird.config import GameConfig
from flappy_bird.domain import World, WorldEvent

from .ports import ControlReading
from .scoring import ScoreBoard


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class GameSession:
    """Coordina el mundo, el récord y los estados de la partida.

    No conoce pygame: recibe comandos (``start``, ``toggle_pause``) y lecturas del
    control, y la UI sólo lee su estado para dibujarlo.
    """

    def __init__(
        self,
        config: GameConfig,
        scoreboard: ScoreBoard,
        world_factory: Callable[[], World] | None = None,
    ) -> None:
        self._config = config
        self._scoreboard = scoreboard
        self._world_factory = world_factory or (lambda: World(config))
        self.world = self._world_factory()
        self.state = GameState.MENU
        self.new_record = False
        self._time_without_signal = 0.0

    # ----------------------------------------------------------------- consultas

    @property
    def best_score(self) -> int:
        return self._scoreboard.best

    @property
    def waiting_for_player(self) -> bool:
        """``True`` mientras se juega pero no se detecta al jugador (juego congelado)."""
        return (
            self.state is GameState.PLAYING
            and self._time_without_signal >= self._config.face_lost_grace
        )

    # ------------------------------------------------------------------ comandos

    def start(self) -> None:
        """Empieza una partida nueva desde el menú o desde game over."""
        if self.state not in (GameState.MENU, GameState.GAME_OVER):
            return
        self.world = self._world_factory()
        self.state = GameState.PLAYING
        self.new_record = False
        self._time_without_signal = 0.0

    def toggle_pause(self) -> None:
        if self.state is GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state is GameState.PAUSED:
            self.state = GameState.PLAYING

    def tick(self, dt: float, reading: ControlReading) -> None:
        if self.state is not GameState.PLAYING:
            return

        if reading.position is None:
            self._time_without_signal += dt
            if self.waiting_for_player:
                return  # se congela hasta que vuelva a detectarse el rostro
            target_y = None
        else:
            self._time_without_signal = 0.0
            target_y = self._to_screen_y(reading.position)

        events = self.world.update(dt, target_y)
        if WorldEvent.CRASHED in events:
            self.state = GameState.GAME_OVER
            self.new_record = self._scoreboard.submit(self.world.score)

    # ------------------------------------------------------------------ internos

    def _to_screen_y(self, position: float) -> float:
        radius = self._config.bird.radius
        usable = self._config.screen.height - 2 * radius
        clamped = min(max(position, 0.0), 1.0)
        return radius + clamped * usable
