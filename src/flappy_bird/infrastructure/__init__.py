"""Capa de infraestructura: implementaciones concretas de los puertos.

Cámara (OpenCV), detección facial (MediaPipe / OpenCV) y persistencia en disco.
Los módulos pesados (cv2, mediapipe) se importan sólo dentro de los submódulos
que los usan, para que el resto del juego y los tests no dependan de ellos.
"""
