"""Detección de la nariz en imágenes de cámara.

Hay dos implementaciones intercambiables de :class:`NoseTracker` (patrón Strategy):

- :class:`~.mediapipe_tracker.MediaPipeNoseTracker`: malla facial de 478 puntos;
  ubica la punta de la nariz real. Precisa y estable (recomendada).
- :class:`~.yunet_tracker.YuNetNoseTracker`: red neuronal YuNet incluida en
  OpenCV; también detecta la nariz real. Modelo incluido en el repo, sirve de
  respaldo sin internet.

:func:`~.factory.create_tracker` elige la mejor disponible.
"""

from .base import NoseTracker, TrackerUnavailableError
from .smoothing import OneEuroFilter, RangeMapper

__all__ = ["NoseTracker", "OneEuroFilter", "RangeMapper", "TrackerUnavailableError"]
