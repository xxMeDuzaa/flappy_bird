"""Descarga (una sola vez) del modelo de MediaPipe Face Landmarker."""

from __future__ import annotations

import logging
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

FACE_LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)
FACE_LANDMARKER_FILENAME = "face_landmarker.task"


def ensure_face_landmarker_model(models_dir: Path, timeout: float = 30.0) -> Path:
    """Devuelve la ruta al modelo, descargándolo si todavía no está en ``models_dir``.

    Lanza ``OSError`` si no existe y no se pudo descargar.
    """
    target = models_dir / FACE_LANDMARKER_FILENAME
    if target.is_file() and target.stat().st_size > 0:
        return target

    models_dir.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(".part")
    logger.info("Descargando modelo de MediaPipe (~4 MB) en %s ...", target)
    with urllib.request.urlopen(FACE_LANDMARKER_URL, timeout=timeout) as response:
        tmp.write_bytes(response.read())
    tmp.replace(target)
    return target
