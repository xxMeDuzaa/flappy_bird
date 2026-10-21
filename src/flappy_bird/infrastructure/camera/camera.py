"""Envoltorio mínimo sobre ``cv2.VideoCapture``."""

from __future__ import annotations

import sys
from typing import Self

import cv2
import numpy as np
from numpy.typing import NDArray

Frame = NDArray[np.uint8]


class CameraError(RuntimeError):
    pass


def _backend() -> int:
    # En Windows DirectShow abre la cámara mucho más rápido que el backend por defecto.
    return int(cv2.CAP_DSHOW) if sys.platform == "win32" else int(cv2.CAP_ANY)


class Camera:
    def __init__(self, capture: cv2.VideoCapture) -> None:
        self._capture = capture

    @classmethod
    def open(cls, index: int = 0, width: int = 640, height: int = 480) -> Self:
        capture = cv2.VideoCapture(index, _backend())
        if not capture.isOpened():
            capture.release()
            raise CameraError(
                f"No se pudo abrir la cámara {index}. "
                "Revisa que esté conectada y que Windows le dé permiso a las apps de escritorio."
            )
        capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        # Buffer mínimo: preferimos el frame más reciente antes que uno atrasado.
        capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return cls(capture)

    def read(self) -> Frame | None:
        ok, frame = self._capture.read()
        if not ok or frame is None:
            return None
        return np.asarray(frame, dtype=np.uint8)

    def release(self) -> None:
        self._capture.release()


def list_cameras(max_index: int = 5) -> list[int]:
    """Devuelve los índices de cámara que se pueden abrir y entregan imagen."""
    found: list[int] = []
    for index in range(max_index):
        capture = cv2.VideoCapture(index, _backend())
        try:
            if capture.isOpened() and capture.read()[0]:
                found.append(index)
        finally:
            capture.release()
    return found
