"""Elige el mejor detector disponible."""

from __future__ import annotations

import importlib.util
import logging
from pathlib import Path
from typing import Literal

from .base import NoseTracker, TrackerUnavailableError

logger = logging.getLogger(__name__)

TrackerKind = Literal["auto", "mediapipe", "opencv"]


def create_tracker(kind: TrackerKind, models_dir: Path) -> NoseTracker:
    """Crea el detector pedido.

    Con ``"auto"`` intenta MediaPipe y, si no está disponible (librería no
    instalada, sin internet para bajar el modelo, etc.), usa YuNet de OpenCV.
    """
    if kind in ("auto", "mediapipe"):
        try:
            return _create_mediapipe(models_dir)
        except TrackerUnavailableError as error:
            if kind == "mediapipe":
                raise
            logger.warning("MediaPipe no disponible (%s). Se usa OpenCV como respaldo.", error)

    from .yunet_tracker import YuNetNoseTracker

    return YuNetNoseTracker()


def _create_mediapipe(models_dir: Path) -> NoseTracker:
    if importlib.util.find_spec("mediapipe") is None:
        raise TrackerUnavailableError("mediapipe no está instalado")
    try:
        from .mediapipe_tracker import MediaPipeNoseTracker
        from .model import ensure_face_landmarker_model
    except ImportError as error:
        raise TrackerUnavailableError(f"falta una dependencia: {error}") from error

    try:
        model_path = ensure_face_landmarker_model(models_dir)
    except OSError as error:
        raise TrackerUnavailableError(f"no se pudo obtener el modelo: {error}") from error

    try:
        return MediaPipeNoseTracker(model_path)
    except TrackerUnavailableError:
        raise
    except Exception as error:  # errores internos de MediaPipe al inicializar
        raise TrackerUnavailableError(f"falló la inicialización: {error}") from error
