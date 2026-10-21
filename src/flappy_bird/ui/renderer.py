"""Dibuja el estado de la sesión en pantalla. No modifica el juego: sólo lo lee."""

from __future__ import annotations

import math

import pygame

from flappy_bird.application import GameSession, GameState, PreviewFrame
from flappy_bird.config import GameConfig
from flappy_bird.domain import Bird, Pipe, World

from . import theme
from .assets import font
from .background import SceneBackground
from .bird_sprite import BirdSprite

MAX_TILT_DEGREES = 25.0
TILT_PER_SPEED = 0.03  # grados por (px/s) de velocidad vertical

#: Velocidad del escenario en el menú (px/s), para que no se vea estático.
MENU_SCROLL_SPEED = 90.0
#: Pájaro del menú: tamaño relativo y vaivén vertical (px, rad/s).
MENU_BIRD_SCALE = 2.2
MENU_BOB_AMPLITUDE = 10.0
MENU_BOB_SPEED = 2.1
#: Pajaritos que muestran el color de cada nivel en el menú.
MENU_LEVEL_BIRD_RADIUS = 10
MENU_LEVEL_SPACING = 76

RIM_OVERHANG = 6
RIM_HEIGHT = 26
PREVIEW_MARGIN = 16


class Renderer:
    def __init__(self, screen: pygame.Surface, config: GameConfig) -> None:
        self._screen = screen
        self._config = config
        self._width, self._height = screen.get_size()

        self._background = SceneBackground((self._width, self._height))

        self._bird_sprite = BirdSprite(config.bird.radius)
        self._menu_bird = BirdSprite(config.bird.radius * MENU_BIRD_SCALE)
        self._menu_time = 0.0
        self._level_birds = [
            BirdSprite(MENU_LEVEL_BIRD_RADIUS, level=i) for i in range(len(config.difficulty))
        ]

        self._dim_overlay = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        self._dim_overlay.fill((0, 0, 0, 140))

    # ------------------------------------------------------------- animación

    def update(self, dt: float, session: GameSession) -> None:
        """Avanza las animaciones (escenario y alas) según el estado de la partida."""
        if session.state is GameState.MENU:
            level, speed = 0, MENU_SCROLL_SPEED
            self._menu_time += dt
            bob_velocity = (
                MENU_BOB_AMPLITUDE * MENU_BOB_SPEED * math.cos(self._menu_time * MENU_BOB_SPEED)
            )
            self._menu_bird.update(dt, bob_velocity)
            for bird in self._level_birds:
                bird.update(dt, 0.0)
        else:
            difficulty = session.world.difficulty
            level = self._config.difficulty.index(difficulty)
            moving = session.state is GameState.PLAYING and not session.waiting_for_player
            speed = difficulty.speed if moving else 0.0
            self._bird_sprite.set_level(level)  # el pájaro se "calienta" con la dificultad
            if moving:  # en pausa o game over las alas (y el color) se quedan quietos
                self._bird_sprite.update(dt, session.world.bird.velocity_y)
        self._background.set_level(level)
        self._background.update(dt, speed)

    # --------------------------------------------------------------- pantallas

    def draw_loading(self, message: str) -> None:
        self._draw_background()
        self._screen.blit(self._dim_overlay, (0, 0))
        self._text_centered(message, 40, theme.WHITE, self._height // 2)

    def render(
        self,
        session: GameSession,
        control_name: str,
        preview: PreviewFrame | None,
    ) -> None:
        self._draw_background()

        if session.state is GameState.MENU:
            self._draw_menu(control_name, session.best_score)
        else:
            self._draw_world(session.world)
            self._draw_hud(session.world.score, session.best_score, session.world)
            if session.state is GameState.PAUSED:
                self._draw_message_overlay("PAUSA", "Presiona P para continuar")
            elif session.waiting_for_player:
                self._draw_message_overlay(
                    "No se detecta tu rostro",
                    "Ubícate frente a la cámara con buena luz para seguir jugando",
                )
            elif session.state is GameState.GAME_OVER:
                self._draw_game_over(session.world.score, session.best_score, session.new_record)

        if preview is not None:
            self._draw_preview(preview)

    # ------------------------------------------------------------------ mundo

    def _draw_background(self) -> None:
        self._background.draw(self._screen)

    def _draw_world(self, world: World) -> None:
        for pipe in world.pipes:
            self._draw_pipe(pipe)
        self._draw_bird(world.bird)

    def _draw_bird(self, bird: Bird) -> None:
        tilt = max(-MAX_TILT_DEGREES, min(MAX_TILT_DEGREES, -bird.velocity_y * TILT_PER_SPEED))
        self._bird_sprite.draw(self._screen, (bird.x, bird.y), tilt)

    def _draw_pipe(self, pipe: Pipe) -> None:
        top, bottom = pipe.top_rect, pipe.bottom_rect
        for rect, rim_y in ((top, top.bottom - RIM_HEIGHT), (bottom, bottom.y)):
            body = pygame.Rect(round(rect.x), round(rect.y), round(rect.width), round(rect.height))
            pygame.draw.rect(self._screen, theme.PIPE_BODY, body)
            highlight = pygame.Rect(body.x + 8, body.y, 10, body.height)
            pygame.draw.rect(self._screen, theme.PIPE_HIGHLIGHT, highlight)
            pygame.draw.rect(self._screen, theme.PIPE_BORDER, body, 2)

            rim = pygame.Rect(
                body.x - RIM_OVERHANG, round(rim_y), body.width + 2 * RIM_OVERHANG, RIM_HEIGHT
            )
            pygame.draw.rect(self._screen, theme.PIPE_RIM, rim, border_radius=8)
            pygame.draw.rect(self._screen, theme.PIPE_BORDER, rim, 2, border_radius=8)

    # -------------------------------------------------------------------- HUD

    def _draw_hud(self, score: int, best: int, world: World) -> None:
        panel = pygame.Rect(20, 20, 190, 92)
        self._panel(panel)
        self._screen.blit(font(48).render(f"Score: {score}", True, theme.WHITE), (32, 30))
        self._screen.blit(font(30).render(f"Récord: {best}", True, theme.YELLOW), (32, 70))

        level = self._config.difficulty.index(world.difficulty) + 1
        self._blit_text(f"Nivel {level}", 26, theme.WHITE, topleft=(panel.x, panel.bottom + 8))

    def _draw_menu(self, control_name: str, best: int) -> None:
        cx = self._width // 2

        self._outlined_text("FLAPPY BIRD", 92, theme.TITLE, (cx, 82), thickness=4)
        self._outlined_text("CONTROL FACIAL", 34, theme.WHITE, (cx, 140), thickness=2)

        bob = math.sin(self._menu_time * MENU_BOB_SPEED) * MENU_BOB_AMPLITUDE
        self._menu_bird.draw(self._screen, (cx, 248 + bob))

        # Los niveles: el pájaro se va "calentando" de amarillo a rojo.
        count = len(self._level_birds)
        strip = pygame.Rect(0, 0, MENU_LEVEL_SPACING * count + 24, 62)
        strip.center = (cx, 372)
        self._panel(strip, radius=14)
        self._blit_text("NIVELES", 20, theme.MUTED, center=(cx, strip.y + 12))
        first_x = cx - MENU_LEVEL_SPACING * (count - 1) / 2
        for i, bird in enumerate(self._level_birds):
            x = first_x + i * MENU_LEVEL_SPACING
            self._blit_text(str(i + 1), 22, theme.WHITE, center=(round(x) - 24, strip.y + 39))
            bird.draw(self._screen, (x + 6, strip.y + 38))

        self._status_badges(control_name, best)

        card = pygame.Rect(0, 0, 680, 140)
        card.midbottom = (cx, self._height - 14)
        self._panel(card)
        pulse = int(160 + math.sin(self._menu_time * 2.5) * 95)
        self._blit_text(
            "PRESIONA CUALQUIER TECLA", 40, theme.WHITE, alpha=pulse, center=(cx, card.y + 32)
        )
        self._blit_text(
            "Mueve la nariz hacia arriba y abajo para guiar al pájaro",
            26,
            theme.MUTED,
            center=(cx, card.y + 70),
        )
        self._key_hints(
            (("P", "Pausa"), ("F11", "Pantalla completa"), ("ESC", "Salir")),
            center=(cx, card.y + 108),
        )

    def _status_badges(self, control_name: str, best: int) -> None:
        """Arriba a la izquierda: con qué se controla el pájaro y el récord actual."""
        x, y = 20, 20
        for dot, label in ((theme.GREEN, control_name), (theme.TITLE, f"Récord: {best}")):
            text = font(26).render(label, True, theme.WHITE)
            badge = pygame.Rect(x, y, text.get_width() + 44, 34)
            self._panel(badge, radius=17)
            pygame.draw.circle(self._screen, dot, (badge.x + 18, badge.centery), 6)
            self._screen.blit(text, text.get_rect(midleft=(badge.x + 32, badge.centery)))
            y = badge.bottom + 8

    def _key_hints(self, hints: tuple[tuple[str, str], ...], center: tuple[int, int]) -> None:
        """Teclas dibujadas como "teclas" (recuadro claro) seguidas de su acción."""
        key_font, label_font = font(24), font(24)
        parts = []
        for key, label in hints:
            key_text = key_font.render(key, True, theme.OUTLINE)
            label_text = label_font.render(label, True, theme.WHITE)
            parts.append((key_text, label_text))
        gap, inner = 28, 8
        total = sum(k.get_width() + 2 * inner + 8 + lbl.get_width() for k, lbl in parts)
        total += gap * (len(parts) - 1)
        x = center[0] - total // 2
        for key_text, label_text in parts:
            cap = pygame.Rect(x, 0, key_text.get_width() + 2 * inner, 28)
            cap.centery = center[1]
            pygame.draw.rect(self._screen, theme.WHITE, cap, border_radius=6)
            self._screen.blit(key_text, key_text.get_rect(center=cap.center))
            label_x = cap.right + 8
            self._screen.blit(label_text, label_text.get_rect(midleft=(label_x, center[1])))
            x = label_x + label_text.get_width() + gap

    def _draw_game_over(self, score: int, best: int, new_record: bool) -> None:
        self._screen.blit(self._dim_overlay, (0, 0))
        mid = self._height // 2
        self._text_centered("GAME OVER", 84, theme.RED, mid - 110)
        if new_record:
            self._text_centered("¡NUEVO RÉCORD!", 42, theme.YELLOW, mid - 50)
        self._text_centered(f"Puntaje: {score}", 40, theme.WHITE, mid + 5)
        self._text_centered(f"Récord: {best}", 40, theme.YELLOW, mid + 45)
        self._text_centered(
            "R o ESPACIO para reiniciar   ·   ESC para salir", 30, theme.WHITE, mid + 115
        )

    def _draw_message_overlay(self, title: str, subtitle: str) -> None:
        self._screen.blit(self._dim_overlay, (0, 0))
        self._text_centered(title, 64, theme.WHITE, self._height // 2 - 20)
        self._text_centered(subtitle, 30, theme.MUTED, self._height // 2 + 35)

    def _draw_preview(self, preview: PreviewFrame) -> None:
        image = pygame.image.frombuffer(preview.rgb, (preview.width, preview.height), "RGB")
        x = self._width - preview.width - PREVIEW_MARGIN
        y = PREVIEW_MARGIN
        self._screen.blit(image, (x, y))

        # Banda de calibración: la zona de la imagen que recorre toda la pantalla.
        tracking = self._config.tracking
        for ratio in (tracking.range_top, tracking.range_bottom):
            line_y = y + round(ratio * preview.height)
            pygame.draw.line(
                self._screen, theme.YELLOW, (x, line_y), (x + preview.width, line_y), 1
            )

        if preview.marker is not None:
            mx = x + round(preview.marker[0] * preview.width)
            my = y + round(preview.marker[1] * preview.height)
            pygame.draw.circle(self._screen, theme.RED, (mx, my), 5)

        border = pygame.Rect(x, y, preview.width, preview.height)
        pygame.draw.rect(self._screen, theme.WHITE, border, 2, border_radius=4)

    # ---------------------------------------------------------------- helpers

    def _panel(self, rect: pygame.Rect, radius: int = 10) -> None:
        """Rectángulo semitransparente. Dibujar con alfa exige una superficie ``SRCALPHA``."""
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            surface, (0, 0, 0, theme.PANEL_ALPHA), surface.get_rect(), border_radius=radius
        )
        pygame.draw.rect(surface, (*theme.WHITE, 220), surface.get_rect(), 2, border_radius=radius)
        self._screen.blit(surface, rect.topleft)

    def _text_centered(self, text: str, size: int, color: theme.Color, center_y: int) -> None:
        self._blit_text(text, size, color, center=(self._width // 2, center_y))

    def _outlined_text(
        self,
        text: str,
        size: int,
        color: theme.Color,
        center: tuple[int, int],
        thickness: int,
    ) -> None:
        """Texto con contorno grueso, en el mismo estilo de dibujo que el pájaro."""
        outline = font(size).render(text, True, theme.OUTLINE)
        rect = outline.get_rect(center=center)
        for dx in range(-thickness, thickness + 1):
            for dy in range(-thickness, thickness + 1):
                if dx * dx + dy * dy <= thickness * thickness:
                    self._screen.blit(outline, rect.move(dx, dy + 1))
        self._screen.blit(font(size).render(text, True, color), rect)

    def _blit_text(
        self, text: str, size: int, color: theme.Color, *, alpha: int = 255, **position: object
    ) -> None:
        """Texto con sombra suave: se lee bien sobre cualquier zona del escenario animado."""
        rendered = font(size).render(text, True, color)
        shadow = font(size).render(text, True, theme.BLACK)
        rect = rendered.get_rect(**position)
        shadow.set_alpha(alpha * 110 // 255)
        rendered.set_alpha(alpha)
        offset = max(1, size // 18)
        self._screen.blit(shadow, rect.move(offset, offset))
        self._screen.blit(rendered, rect)
