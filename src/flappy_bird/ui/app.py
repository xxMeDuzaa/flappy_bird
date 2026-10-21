"""Loop principal: traduce eventos de pygame a comandos de la sesión y dibuja cada frame."""

from __future__ import annotations

import pygame

from flappy_bird.application import ControlSource, GameSession, GameState, PreviewSource
from flappy_bird.config import GameConfig

from .renderer import Renderer

#: Paso máximo de simulación (s). Si la ventana se congela (p. ej. al arrastrarla),
#: evita que al volver el mundo "salte" y el pájaro atraviese un tubo.
MAX_FRAME_TIME = 0.05

RESTART_KEYS = frozenset({pygame.K_r, pygame.K_SPACE, pygame.K_RETURN})


class GameApp:
    def __init__(
        self,
        config: GameConfig,
        session: GameSession,
        renderer: Renderer,
        control: ControlSource,
        preview: PreviewSource | None = None,
    ) -> None:
        self._config = config
        self._session = session
        self._renderer = renderer
        self._control = control
        self._preview = preview
        self._clock = pygame.time.Clock()
        self._running = False

    def run(self) -> None:
        self._running = True
        self._control.start()
        try:
            while self._running:
                dt = min(self._clock.tick(self._config.screen.fps) / 1000.0, MAX_FRAME_TIME)
                for event in pygame.event.get():
                    self._handle_event(event)
                self._session.tick(dt, self._control.read())
                self._renderer.update(dt, self._session)
                preview = self._preview.latest_preview() if self._preview else None
                self._renderer.render(self._session, self._control.name, preview)
                pygame.display.flip()
        finally:
            self._control.close()

    def _handle_event(self, event: pygame.event.Event) -> None:
        session = self._session
        if event.type == pygame.QUIT:
            self._running = False
        elif event.type == pygame.WINDOWFOCUSLOST and session.state is GameState.PLAYING:
            session.toggle_pause()
        elif event.type == pygame.MOUSEBUTTONDOWN and session.state is GameState.MENU:
            session.start()
        elif event.type == pygame.KEYDOWN:
            self._handle_key(event.key)

    def _handle_key(self, key: int) -> None:
        session = self._session
        if key == pygame.K_ESCAPE:
            self._running = False
        elif key == pygame.K_F11:
            pygame.display.toggle_fullscreen()
        elif session.state is GameState.MENU or (
            session.state is GameState.GAME_OVER and key in RESTART_KEYS
        ):
            session.start()
        elif key == pygame.K_p:
            session.toggle_pause()
