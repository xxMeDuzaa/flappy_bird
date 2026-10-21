"""Dibuja el estado de la sesión en pantalla. No modifica el juego: sólo lo lee."""

from __future__ import annotations

import math

import pygame

from flappy_bird.application import GameSession, GameState, PreviewFrame
from flappy_bird.config import GameConfig
from flappy_bird.domain import Bird, Pipe, World

from . import theme
from .assets import font, load_image

#: Cuánto más grande que la hitbox se dibuja el sprite. La hitbox es un poco más
#: chica que el dibujo a propósito: se siente más justo para el jugador.
SPRITE_SCALE = 1.5
MAX_TILT_DEGREES = 25.0
TILT_PER_SPEED = 0.03  # grados por (px/s) de velocidad vertical

RIM_OVERHANG = 6
RIM_HEIGHT = 26
PREVIEW_MARGIN = 16


class Renderer:
    def __init__(self, screen: pygame.Surface, config: GameConfig) -> None:
        self._screen = screen
        self._config = config
        self._width, self._height = screen.get_size()

        background = load_image("background.jpg", alpha=False)
        self._background = (
            pygame.transform.smoothscale(background, (self._width, self._height))
            if background is not None
            else None
        )

        sprite = load_image("bird.png")
        if sprite is not None:
            target_w = round(config.bird.radius * 2 * SPRITE_SCALE)
            target_h = round(sprite.get_height() * target_w / sprite.get_width())
            # ``scale`` (vecino más cercano) mantiene nítido el pixel art.
            sprite = pygame.transform.scale(sprite, (target_w, target_h))
        self._bird_sprite = sprite
        self._menu_sprite = pygame.transform.scale_by(sprite, 2) if sprite is not None else None

        self._dim_overlay = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        self._dim_overlay.fill((0, 0, 0, 140))

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
            self._draw_menu(control_name)
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
        if self._background is not None:
            self._screen.blit(self._background, (0, 0))
        else:
            self._screen.fill(theme.SKY)

    def _draw_world(self, world: World) -> None:
        for pipe in world.pipes:
            self._draw_pipe(pipe)
        self._draw_bird(world.bird)

    def _draw_bird(self, bird: Bird) -> None:
        if self._bird_sprite is None:
            self._draw_fallback_bird(bird.x, bird.y, bird.radius)
            return
        tilt = max(-MAX_TILT_DEGREES, min(MAX_TILT_DEGREES, -bird.velocity_y * TILT_PER_SPEED))
        sprite = (
            pygame.transform.rotate(self._bird_sprite, tilt)
            if abs(tilt) > 0.5
            else self._bird_sprite
        )
        self._screen.blit(sprite, sprite.get_rect(center=(round(bird.x), round(bird.y))))

    def _draw_fallback_bird(self, x: float, y: float, radius: float) -> None:
        cx, cy, r = round(x), round(y), round(radius)
        pygame.draw.circle(self._screen, theme.YELLOW, (cx, cy), r)
        pygame.draw.circle(self._screen, theme.BLACK, (cx, cy), r, 2)
        pygame.draw.circle(self._screen, theme.BLACK, (cx + r // 2, cy - r // 3), max(3, r // 5))
        beak = [(cx + r, cy), (cx + r + r // 2, cy), (cx + r, cy + r // 4)]
        pygame.draw.polygon(self._screen, theme.ORANGE, beak)

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
        label = font(26).render(f"Nivel {level}", True, theme.MUTED)
        self._screen.blit(label, (panel.x, panel.bottom + 8))

    def _draw_menu(self, control_name: str) -> None:
        cx = self._width // 2
        cy = self._height // 2 + 30

        for i in range(3):  # halo detrás del pájaro
            radius = 100 - i * 20
            halo = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(halo, (*theme.VIOLET, 90 - i * 25), (radius, radius), radius)
            self._screen.blit(halo, (cx - radius, cy - radius))

        if self._menu_sprite is not None:
            bob = math.sin(pygame.time.get_ticks() / 300) * 8
            self._screen.blit(
                self._menu_sprite, self._menu_sprite.get_rect(center=(cx, round(cy + bob)))
            )
        else:
            self._draw_fallback_bird(cx, cy, 40)

        title = font(84)
        shadow = title.render("FLAPPY BIRD", True, theme.YELLOW_SHADOW)
        text = title.render("FLAPPY BIRD", True, theme.YELLOW)
        self._screen.blit(shadow, shadow.get_rect(center=(cx + 3, 103)))
        self._screen.blit(text, text.get_rect(center=(cx, 100)))
        self._text_centered("CONTROL FACIAL", 34, theme.WHITE, 155)

        pulse = int(160 + math.sin(pygame.time.get_ticks() / 400) * 95)
        prompt = font(38).render("PRESIONA CUALQUIER TECLA", True, theme.WHITE)
        prompt.set_alpha(pulse)
        self._screen.blit(prompt, prompt.get_rect(center=(cx, self._height - 105)))

        self._text_centered(
            "Mueve la nariz hacia arriba y abajo para guiar al pájaro",
            26,
            theme.WHITE,
            self._height - 62,
        )
        self._text_centered(
            f"Control: {control_name}   ·   P: pausa   ·   F11: pantalla completa   ·   ESC: salir",
            22,
            theme.MUTED,
            self._height - 30,
        )

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

    def _panel(self, rect: pygame.Rect) -> None:
        """Rectángulo semitransparente. Dibujar con alfa exige una superficie ``SRCALPHA``."""
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            surface, (0, 0, 0, theme.PANEL_ALPHA), surface.get_rect(), border_radius=10
        )
        pygame.draw.rect(surface, (*theme.WHITE, 220), surface.get_rect(), 2, border_radius=10)
        self._screen.blit(surface, rect.topleft)

    def _text_centered(self, text: str, size: int, color: theme.Color, center_y: int) -> None:
        rendered = font(size).render(text, True, color)
        self._screen.blit(rendered, rendered.get_rect(center=(self._width // 2, center_y)))
