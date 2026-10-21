"""Detector basado en MediaPipe Face Landmarker (API *Tasks*)."""

from __future__ import annotations

import time
from pathlib import Path

import cv2
import numpy as np
from numpy.typing import NDArray

from .base import TrackerUnavailableError

#: Índice de la punta de la nariz en la malla facial de MediaPipe.
NOSE_TIP_LANDMARK = 1


class MediaPipeNoseTracker:
    name = "MediaPipe Face Landmarker"

    def __init__(self, model_path: Path) -> None:
        try:
            import mediapipe as mp
        except ImportError as error:  # pragma: no cover - depende del entorno
            raise TrackerUnavailableError("mediapipe no está instalado") from error

        self._mp = mp
        vision = mp.tasks.vision
        options = vision.FaceLandmarkerOptions(
            # Se pasa el modelo como bytes: evita problemas con rutas con tildes en Windows.
            base_options=mp.tasks.BaseOptions(model_asset_buffer=model_path.read_bytes()),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            min_tracking_confidence=0.5,
        )
        self._landmarker = vision.FaceLandmarker.create_from_options(options)
        self._last_timestamp_ms = -1

    def locate(self, frame_bgr: NDArray[np.uint8]) -> tuple[float, float] | None:
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        image = self._mp.Image(image_format=self._mp.ImageFormat.SRGB, data=rgb)
        # En modo VIDEO los timestamps tienen que ser estrictamente crecientes.
        timestamp_ms = max(time.monotonic_ns() // 1_000_000, self._last_timestamp_ms + 1)
        self._last_timestamp_ms = timestamp_ms

        result = self._landmarker.detect_for_video(image, timestamp_ms)
        if not result.face_landmarks:
            return None
        nose = result.face_landmarks[0][NOSE_TIP_LANDMARK]
        return float(nose.x), float(nose.y)

    def close(self) -> None:
        self._landmarker.close()
