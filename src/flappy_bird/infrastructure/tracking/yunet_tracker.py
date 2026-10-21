"""Detector de respaldo: red neuronal YuNet incluida en OpenCV (``cv2.FaceDetectorYN``).

Detecta la cara y 5 puntos clave (ojos, nariz y comisuras de la boca), así que
ubica la nariz real en vez de estimarla. El modelo ONNX (~230 KB, licencia MIT)
viene incluido en ``assets/models``, por lo que funciona sin internet.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from numpy.typing import NDArray

from .base import TrackerUnavailableError

MODEL_PATH = (
    Path(__file__).resolve().parents[2] / "assets" / "models" / "face_detection_yunet_2023mar.onnx"
)

# Columnas de cada detección: x, y, w, h, ojo der. (x, y), ojo izq. (x, y),
# nariz (x, y), boca der. (x, y), boca izq. (x, y), confianza.
_NOSE_X, _NOSE_Y = 8, 9


class YuNetNoseTracker:
    name = "OpenCV YuNet"

    def __init__(self, model_path: Path = MODEL_PATH, score_threshold: float = 0.7) -> None:
        if not model_path.is_file():
            raise TrackerUnavailableError(f"No se encontró el modelo {model_path}")
        try:
            self._detector = cv2.FaceDetectorYN.create(
                str(model_path), "", (320, 240), score_threshold, 0.3, 5
            )
        except (AttributeError, cv2.error) as error:
            raise TrackerUnavailableError(f"OpenCV no pudo cargar YuNet: {error}") from error
        self._input_size: tuple[int, int] = (320, 240)

    def locate(self, frame_bgr: NDArray[np.uint8]) -> tuple[float, float] | None:
        height, width = frame_bgr.shape[:2]
        if (width, height) != self._input_size:
            self._detector.setInputSize((width, height))
            self._input_size = (width, height)

        _, faces = self._detector.detect(frame_bgr)
        if faces is None or len(faces) == 0:
            return None
        # La cara más grande es la del jugador (la más cercana a la cámara).
        face = max(faces, key=lambda row: float(row[2]) * float(row[3]))
        return float(face[_NOSE_X]) / width, float(face[_NOSE_Y]) / height

    def close(self) -> None:
        pass
