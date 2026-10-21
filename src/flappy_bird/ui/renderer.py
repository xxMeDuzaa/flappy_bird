"""Dibuja el estado de la sesión en pantalla. No modifica el juego: sólo lo lee."""

from __future__ import annotations

import math

import pygame

from flappy_bird.application import GameSession, GameState, PreviewFrame
from flappy_bird.config import GameConfig
from flappy_bird.domain import Bird, Pipe, World

from . import theme
from .assets import render_outlined_text, render_text
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
#: Tamaño de cada píxel del pájaro grande del menú (el del juego usa 2).
MENU_BIRD_PIXEL = 3
#: Pajaritos que muestran el color de cada nivel en el menú.
MENU_LEVEL_BIRD_RADIUS = 10
MENU_LEVEL_SPACING = 76
#: Transparencia del recuadro de instrucciones del menú (más sutil que el resto).
SUBTLE_PANEL_ALPHA = 45

RIM_OVERHANG = 6
RIM_HEIGHT = 26
PIPE_OUTLINE = 3
PREVIEW_MARGIN = 16


class Renderer:
    def __init__(self, screen: pygame.Surface, config: GameConfig) -> None:
        self._screen = screen
        self._config = config
        self._width, self._height = screen.get_size()

        self._background = SceneBackground((self._width, self._height))

        self._bird_sprite = BirdSprite(config.bird.radius)
        self._menu_bird = BirdSprite(
            config.bird.radius * MENU_BIRD_SCALE, pixel_size=MENU_BIRD_PIXEL
        )
        self._menu_time = 0.0
        self._level_birds = [
            BirdSprite(MENU_LEVEL_BIRD_RADIUS, level=i, pixel_size=1)
            for i in range(len(config.difficulty))
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
        self._title(message, 5, theme.WHITE, (self._width // 2, self._height // 2))

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
                self._draw_message_overlay(
                    "PAUSA", None, ((("P",), "Continuar"), (("ESC",), "Salir"))
                )
            elif session.waiting_for_player:
                self._draw_message_overlay(
                    "No se detecta tu rostro",
                    "Ubicate frente a la camara con buena luz para seguir jugando",
                    ((("P",), "Pausa"), (("ESC",), "Salir")),
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
        """Tubos con el mismo estilo de dibujo que el pájaro: contorno oscuro grueso y volumen."""
        top, bottom = pipe.top_rect, pipe.bottom_rect
        for rect, rim_y in ((top, top.bottom - RIM_HEIGHT), (bottom, bottom.y)):
            body = pygame.Rect(round(rect.x), round(rect.y), round(rect.width), round(rect.height))
            self._shaded_block(body, radius=0)
            rim = pygame.Rect(
                body.x - RIM_OVERHANG, round(rim_y), body.width + 2 * RIM_OVERHANG, RIM_HEIGHT
            )
            self._shaded_block(rim, radius=6)

    def _shaded_block(self, rect: pygame.Rect, radius: int) -> None:
        """Rectángulo verde con luz a la izquierda, sombra a la derecha y contorno."""
        pygame.draw.rect(self._screen, theme.PIPE_BODY, rect, border_radius=radius)
        light = pygame.Rect(rect.x + 8, rect.y, 10, rect.height)
        shade = pygame.Rect(rect.right - 18, rect.y, 12, rect.height)
        self._screen.fill(theme.PIPE_HIGHLIGHT, light.clip(rect))
        self._screen.fill(theme.PIPE_SHADE, shade.clip(rect))
        pygame.draw.rect(self._screen, theme.OUTLINE, rect, PIPE_OUTLINE, border_radius=radius)

    # -------------------------------------------------------------------- HUD

    def _draw_hud(self, score: int, best: int, world: World) -> None:
        """Puntaje, récord y nivel con el mismo formato de "píldora" que el menú."""
        level = self._config.difficulty.index(world.difficulty) + 1
        self._badges(
            (
                (theme.WHITE, f"Score {score}"),
                (theme.TITLE, f"Record {best}"),
                # El punto del nivel toma el color actual del pájaro.
                (self._bird_sprite.colors.body, f"Nivel {level}"),
            )
        )

    def _draw_menu(self, control_name: str, best: int) -> None:
        cx = self._width // 2

        self._title("FLAPPY BIRD", 8, theme.TITLE, (cx, 96))
        subtitle = render_outlined_text(3, "EUREKAS 2026", theme.WHITE, theme.OUTLINE, 3, 0)
        self._screen.blit(subtitle, subtitle.get_rect(center=(cx, 160)))

        bob = math.sin(self._menu_time * MENU_BOB_SPEED) * MENU_BOB_AMPLITUDE
        self._menu_bird.draw(self._screen, (cx, 258 + bob))

        # Los niveles: el pájaro se va "calentando" de amarillo a rojo.
        count = len(self._level_birds)
        strip = pygame.Rect(0, 0, MENU_LEVEL_SPACING * count + 24, 64)
        strip.center = (cx, 372)
        self._panel(strip, radius=14, border=False)
        self._blit_text("NIVELES", 2, theme.MUTED, center=(cx, strip.y + 14))
        first_x = cx - MENU_LEVEL_SPACING * (count - 1) / 2
        for i, bird in enumerate(self._level_birds):
            x = first_x + i * MENU_LEVEL_SPACING
            self._blit_text(str(i + 1), 2, theme.WHITE, center=(round(x) - 24, strip.y + 42))
            bird.draw(self._screen, (x + 6, strip.y + 41))

        self._status_badges(control_name, best)

        # Instrucciones: discretas, sin recuadro marcado, para no competir con el título.
        card = pygame.Rect(0, 0, 600, 104)
        card.midbottom = (cx, self._height - 12)
        self._panel(card, radius=14, alpha=SUBTLE_PANEL_ALPHA, border=False)
        pulse = int(170 + math.sin(self._menu_time * 2.5) * 85)
        self._blit_text(
            "Presiona cualquier tecla", 3, theme.WHITE, alpha=pulse, center=(cx, card.y + 24)
        )
        self._blit_text(
            "Mueve la nariz para guiar al pajaro", 2, theme.MUTED, center=(cx, card.y + 54)
        )
        self._key_hints(
            ((("P",), "Pausa"), (("F11",), "Pantalla completa"), (("ESC",), "Salir")),
            center=(cx, card.y + 82),
        )

    def _status_badges(self, control_name: str, best: int) -> None:
        """Arriba a la izquierda: con qué se controla el pájaro y el récord actual."""
        self._badges(((theme.GREEN, control_name), (theme.TITLE, f"Record {best}")))

    def _badges(self, items: tuple[tuple[theme.Color, str], ...]) -> None:
        """Columna de "píldoras" arriba a la izquierda: un punto de color y un texto."""
        x, y = 20, 20
        for dot, label in items:
            text = render_text(2, label, theme.WHITE)
            badge = pygame.Rect(x, y, text.get_width() + 46, 32)
            self._panel(badge, radius=16)
            pygame.draw.circle(self._screen, dot, (badge.x + 18, badge.centery), 6)
            self._screen.blit(text, text.get_rect(midleft=(badge.x + 32, badge.centery)))
            y = badge.bottom + 8

    def _key_hints(
        self, hints: tuple[tuple[tuple[str, ...], str], ...], center: tuple[int, int]
    ) -> None:
        """Teclas dibujadas como "teclas" (recuadro claro) seguidas de su acción.

        Cada ayuda es ``(teclas, acción)``; varias teclas para la misma acción se
        dibujan una al lado de la otra.
        """
        cap_gap, inner, after_keys, gap = 6, 6, 8, 26
        groups = [
            (
                [render_text(2, key, theme.OUTLINE) for key in keys],
                render_text(2, label, theme.MUTED),
            )
            for keys, label in hints
        ]

        def group_width(keys: list[pygame.Surface], label: pygame.Surface) -> int:
            caps = sum(k.get_width() + 2 * inner for k in keys) + cap_gap * (len(keys) - 1)
            return int(caps + after_keys + label.get_width())

        total = sum(group_width(k, lbl) for k, lbl in groups) + gap * (len(groups) - 1)
        x = center[0] - total // 2
        for keys, label in groups:
            for key_text in keys:
                cap = pygame.Rect(x, 0, key_text.get_width() + 2 * inner, key_text.get_height() + 8)
                cap.centery = center[1]
                pygame.draw.rect(self._screen, theme.MUTED, cap, border_radius=4)
                self._screen.blit(key_text, key_text.get_rect(center=cap.center))
                x = cap.right + cap_gap
            x += after_keys - cap_gap
            self._screen.blit(label, label.get_rect(midleft=(x, center[1])))
            x += label.get_width() + gap

    def _draw_game_over(self, score: int, best: int, new_record: bool) -> None:
        self._screen.blit(self._dim_overlay, (0, 0))
        cx, mid = self._width // 2, self._height // 2
        self._title("GAME OVER", 8, theme.RED, (cx, mid - 110))
        if new_record:
            self._text_centered("Nuevo record!", 3, theme.TITLE, mid - 40)
        self._text_centered(f"Puntaje {score}", 4, theme.WHITE, mid + 10)
        self._text_centered(f"Record {best}", 3, theme.TITLE, mid + 52)
        self._key_hints(
            ((("R", "ESPACIO"), "Reiniciar"), (("ESC",), "Salir")), center=(cx, mid + 120)
        )

    def _draw_message_overlay(
        self,
        title: str,
        subtitle: str | None,
        hints: tuple[tuple[tuple[str, ...], str], ...],
    ) -> None:
        self._screen.blit(self._dim_overlay, (0, 0))
        cx, mid = self._width // 2, self._height // 2
        # Escala 6 si entra cómodo; si no, 5 (los títulos largos no deben tocar los bordes).
        scale = 6 if len(title) * 6 * 6 < self._width - 160 else 5
        self._title(title, scale, theme.WHITE, (cx, mid - 40))
        if subtitle:
            self._text_centered(subtitle, 2, theme.MUTED, mid + 20)
        self._key_hints(hints, center=(cx, mid + 60))

    def _draw_preview(self, preview: PreviewFrame) -> None:
        """Vista de la cámara dentro de un recuadro como el resto de la interfaz."""
        pad, header = 8, 28
        card = pygame.Rect(0, 0, preview.width + 2 * pad, preview.height + pad + header)
        card.topright = (self._width - PREVIEW_MARGIN, PREVIEW_MARGIN)
        self._panel(card, radius=14, border=False)

        dot_color = theme.GREEN if preview.marker is not None else theme.RED
        pygame.draw.circle(self._screen, dot_color, (card.x + pad + 8, card.y + header // 2 + 2), 6)
        label = render_text(2, "Camara", theme.WHITE)
        self._screen.blit(
            label, label.get_rect(midleft=(card.x + pad + 22, card.y + header // 2 + 2))
        )

        x, y = card.x + pad, card.y + header
        image = pygame.image.frombuffer(preview.rgb, (preview.width, preview.height), "RGB")
        self._screen.blit(image, (x, y))

        # Banda de calibración: la zona de la imagen que recorre toda la pantalla.
        tracking = self._config.tracking
        for ratio in (tracking.range_top, tracking.range_bottom):
            line_y = y + round(ratio * preview.height)
            pygame.draw.line(self._screen, theme.TITLE, (x, line_y), (x + preview.width, line_y), 1)

        if preview.marker is not None:
            mx = x + round(preview.marker[0] * preview.width)
            my = y + round(preview.marker[1] * preview.height)
            pygame.draw.circle(self._screen, theme.OUTLINE, (mx, my), 7)
            pygame.draw.circle(self._screen, theme.RED, (mx, my), 5)

        frame = pygame.Rect(x, y, preview.width, preview.height)
        pygame.draw.rect(self._screen, theme.OUTLINE, frame, 2, border_radius=4)

    # ---------------------------------------------------------------- helpers

    def _panel(
        self,
        rect: pygame.Rect,
        radius: int = 10,
        alpha: int = theme.PANEL_ALPHA,
        border: bool = True,
    ) -> None:
        """Rectángulo semitransparente. Dibujar con alfa exige una superficie ``SRCALPHA``."""
        surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surface, (0, 0, 0, alpha), surface.get_rect(), border_radius=radius)
        if border:
            pygame.draw.rect(
                surface, (*theme.WHITE, 220), surface.get_rect(), 2, border_radius=radius
            )
        self._screen.blit(surface, rect.topleft)

    def _text_centered(self, text: str, scale: int, color: theme.Color, center_y: int) -> None:
        self._blit_text(text, scale, color, center=(self._width // 2, center_y))

    def _title(self, text: str, scale: int, color: theme.Color, center: tuple[int, int]) -> None:
        """Título grande "relleno": contorno grueso y relieve, como en los arcades."""
        surface = render_outlined_text(
            scale, text, color, theme.OUTLINE, thickness=scale, depth=scale
        )
        self._screen.blit(surface, surface.get_rect(center=center))

    def _blit_text(
        self, text: str, scale: int, color: theme.Color, *, alpha: int = 255, **position: object
    ) -> None:
        """Texto con sombra de un "píxel": se lee bien sobre el escenario animado."""
        rendered = render_text(scale, text, color)
        shadow = render_text(scale, text, theme.BLACK)
        if alpha < 255:  # las superficies están cacheadas: se copian antes de modificarlas
            rendered, shadow = rendered.copy(), shadow.copy()
            rendered.set_alpha(alpha)
        else:
            shadow = shadow.copy()
        shadow.set_alpha(alpha * 120 // 255)
        rect = rendered.get_rect(**position)
        self._screen.blit(shadow, rect.move(scale, scale))
        self._screen.blit(rendered, rect)
