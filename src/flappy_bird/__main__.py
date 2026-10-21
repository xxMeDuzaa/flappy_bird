"""Punto de entrada: ``python -m flappy_bird`` o el comando ``flappy-bird``.

Este módulo es la *composition root*: el único lugar que conoce todas las
implementaciones concretas y las conecta entre sí (inyección de dependencias).
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Sequence
from pathlib import Path

import pygame

from flappy_bird import __version__
from flappy_bird.application import ControlSource, GameSession, PreviewSource, ScoreBoard
from flappy_bird.config import GameConfig, TrackingConfig
from flappy_bird.infrastructure.paths import user_data_dir
from flappy_bird.infrastructure.storage import JsonHighScoreRepository
from flappy_bird.ui.app import GameApp
from flappy_bird.ui.mouse_control import MouseControl
from flappy_bird.ui.renderer import Renderer

logger = logging.getLogger("flappy_bird")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="flappy-bird",
        description="Flappy Bird controlado con la nariz a través de la cámara.",
    )
    parser.add_argument(
        "--control",
        choices=("face", "mouse"),
        default="face",
        help="cómo se controla el pájaro (por defecto: face)",
    )
    parser.add_argument(
        "--tracker",
        choices=("auto", "mediapipe", "opencv"),
        default="auto",
        help="detector facial; 'auto' usa MediaPipe y cae a OpenCV si no está disponible",
    )
    parser.add_argument(
        "--camera", type=int, default=0, help="índice de la cámara (por defecto: 0)"
    )
    parser.add_argument("--no-preview", action="store_true", help="ocultar la vista de la cámara")
    parser.add_argument("-v", "--verbose", action="store_true", help="mostrar logs de depuración")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser.parse_args(argv)


def create_control(
    args: argparse.Namespace, config: GameConfig, data_dir: Path
) -> tuple[ControlSource, PreviewSource | None]:
    """Crea el control pedido. Si la cámara no está disponible, cae al mouse."""
    mouse = MouseControl(config.screen.height)
    if args.control == "mouse":
        return mouse, None

    # Import diferido: OpenCV/MediaPipe sólo se cargan si se usa la cámara.
    from flappy_bird.infrastructure.camera import Camera, CameraError
    from flappy_bird.infrastructure.face_control import FaceControl
    from flappy_bird.infrastructure.tracking import TrackerUnavailableError
    from flappy_bird.infrastructure.tracking.factory import create_tracker

    tracking = config.tracking
    try:
        camera = Camera.open(tracking.camera_index, tracking.frame_width, tracking.frame_height)
    except CameraError as error:
        logger.error("%s", error)
        logger.warning("Se usará el mouse para controlar el pájaro.")
        return mouse, None

    try:
        tracker = create_tracker(args.tracker, data_dir / "models")
    except TrackerUnavailableError as error:
        camera.release()
        raise SystemExit(f"No se pudo iniciar el detector '{args.tracker}': {error}") from error
    logger.info("Detector facial: %s", tracker.name)

    face = FaceControl(camera, tracker, tracking)
    return face, (None if args.no_preview else face)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)-8s %(name)s: %(message)s",
    )

    config = GameConfig(tracking=TrackingConfig(camera_index=args.camera))
    data_dir = user_data_dir()
    repository = JsonHighScoreRepository(data_dir / "highscore.json")
    logger.debug("Récord guardado en %s", repository.path)

    pygame.init()
    try:
        screen = pygame.display.set_mode((config.screen.width, config.screen.height), pygame.SCALED)
        pygame.display.set_caption(config.screen.title)
        renderer = Renderer(screen, config)

        renderer.draw_loading("Iniciando camara...")
        pygame.display.flip()
        pygame.event.pump()

        control, preview = create_control(args, config, data_dir)
        session = GameSession(config, ScoreBoard(repository))
        GameApp(config, session, renderer, control, preview).run()
    except KeyboardInterrupt:
        pass
    finally:
        pygame.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
