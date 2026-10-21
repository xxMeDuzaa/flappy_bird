"""Herramienta de diagnóstico de la cámara y del detector facial (sin el juego).

Uso:
    python tools/camera_debug.py                 # ventana con la detección en vivo
    python tools/camera_debug.py --list-cameras  # qué índices de cámara funcionan
    python tools/camera_debug.py --tracker opencv --camera 1
"""

from __future__ import annotations

import argparse
import logging
import time

import cv2

from flappy_bird.config import TrackingConfig
from flappy_bird.infrastructure.camera import Camera, CameraError, list_cameras
from flappy_bird.infrastructure.paths import user_data_dir
from flappy_bird.infrastructure.tracking import OneEuroFilter, RangeMapper
from flappy_bird.infrastructure.tracking.factory import create_tracker

WINDOW = "Flappy Bird - debug de camara (ESC para salir)"
GREEN = (0, 255, 0)
YELLOW = (0, 220, 255)
RED = (0, 0, 255)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--tracker", choices=("auto", "mediapipe", "opencv"), default="auto")
    parser.add_argument("--list-cameras", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)-8s %(message)s")

    if args.list_cameras:
        found = list_cameras()
        print("Cámaras disponibles:", ", ".join(map(str, found)) if found else "ninguna")
        return 0

    config = TrackingConfig(camera_index=args.camera)
    try:
        camera = Camera.open(config.camera_index, config.frame_width, config.frame_height)
    except CameraError as error:
        print(error)
        return 1

    tracker = create_tracker(args.tracker, user_data_dir() / "models")
    mapper = RangeMapper(config.range_top, config.range_bottom)
    smoother = OneEuroFilter(config.filter_min_cutoff, config.filter_beta)
    print(f"Detector: {tracker.name}")

    last = time.perf_counter()
    fps = 0.0
    try:
        while True:
            frame = camera.read()
            if frame is None:
                continue
            frame = cv2.flip(frame, 1)
            h, w = frame.shape[:2]
            nose = tracker.locate(frame)

            for ratio in (config.range_top, config.range_bottom):
                cv2.line(frame, (0, int(ratio * h)), (w, int(ratio * h)), YELLOW, 1)

            if nose is not None:
                position = smoother(mapper(nose[1]), time.monotonic())
                cv2.circle(frame, (int(nose[0] * w), int(nose[1] * h)), 7, RED, -1)
                text = f"nariz y={nose[1]:.2f}  ->  posicion en juego={position:.2f}"
                cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, GREEN, 2)
            else:
                smoother.reset()
                cv2.putText(frame, "Sin rostro", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, RED, 2)

            now = time.perf_counter()
            fps = 0.9 * fps + 0.1 * (1.0 / max(now - last, 1e-6))
            last = now
            label = f"{tracker.name}  |  {fps:.0f} FPS"
            cv2.putText(frame, label, (10, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN, 1)

            cv2.imshow(WINDOW, frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break
    finally:
        camera.release()
        tracker.close()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
