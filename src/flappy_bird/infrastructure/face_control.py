"""Control por nariz: cámara + detector + filtrado, corriendo en un hilo propio.

Leer la cámara bloquea hasta que llega el próximo frame (~33 ms a 30 FPS) y
la detección facial también tarda. Si eso pasara en el loop del juego, los FPS
del juego quedarían atados a los de la cámara. Por eso todo el procesamiento
corre en un hilo de fondo y el juego sólo consulta la última lectura disponible.
"""

from __future__ import annotations

import logging
import threading
import time

import cv2
import numpy as np

from flappy_bird.application.ports import NO_SIGNAL, ControlReading, PreviewFrame
from flappy_bird.config import TrackingConfig

from .camera import Camera
from .tracking import NoseTracker, OneEuroFilter, RangeMapper

logger = logging.getLogger(__name__)


class FaceControl:
    """Implementa los puertos ``ControlSource`` y ``PreviewSource``."""

    def __init__(self, camera: Camera, tracker: NoseTracker, config: TrackingConfig) -> None:
        self._camera = camera
        self._tracker = tracker
        self._config = config
        self._mapper = RangeMapper(config.range_top, config.range_bottom)
        self._filter = OneEuroFilter(config.filter_min_cutoff, config.filter_beta)

        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._position: float | None = None
        self._updated_at = 0.0
        self._preview: PreviewFrame | None = None

    @property
    def name(self) -> str:
        return f"Cámara ({self._tracker.name})"

    # ------------------------------------------------------------ ciclo de vida

    def start(self) -> None:
        if self._thread is not None:
            return
        self._thread = threading.Thread(target=self._run, name="face-control", daemon=True)
        self._thread.start()

    def close(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        self._camera.release()
        self._tracker.close()

    # --------------------------------------------------------------- consultas

    def read(self) -> ControlReading:
        with self._lock:
            position, updated_at = self._position, self._updated_at
        if position is None or time.monotonic() - updated_at > self._config.stale_after:
            return NO_SIGNAL
        return ControlReading(position=position)

    def latest_preview(self) -> PreviewFrame | None:
        with self._lock:
            return self._preview

    # ------------------------------------------------------------- hilo worker

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self._process_next_frame()
            except Exception:  # un error puntual no debe matar el hilo
                logger.exception("Error procesando un frame de la cámara")
                time.sleep(0.1)

    def _process_next_frame(self) -> None:
        frame = self._camera.read()
        if frame is None:
            time.sleep(0.01)
            return
        if self._config.mirror:
            frame = np.ascontiguousarray(frame[:, ::-1])

        nose = self._tracker.locate(frame)
        now = time.monotonic()
        if nose is None:
            position = None
            self._filter.reset()  # al reaparecer la cara no arrastramos la posición vieja
        else:
            position = self._filter(self._mapper(nose[1]), now)

        width, height = self._config.preview_size
        small = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        rgb = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        preview = PreviewFrame(width=width, height=height, rgb=rgb.tobytes(), marker=nose)

        with self._lock:
            self._position = position
            self._updated_at = now
            self._preview = preview
