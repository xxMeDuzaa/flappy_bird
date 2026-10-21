"""Configuración centralizada del juego.

Todas las constantes "mágicas" del juego viven acá, como dataclasses inmutables.
Así hay una única fuente de verdad y cualquier capa (dominio, UI, entrada) puede
recibir la configuración por parámetro, lo que facilita los tests.

Las velocidades se expresan en píxeles por **segundo** (no por frame), de modo que
el juego se comporta igual sin importar los FPS reales.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ScreenConfig:
    width: int = 1024
    height: int = 600
    fps: int = 60
    title: str = "Flappy Bird - Control Facial"


@dataclass(frozen=True, slots=True)
class BirdConfig:
    #: Posición horizontal fija del pájaro como fracción del ancho de pantalla.
    x_ratio: float = 0.25
    #: Radio de la hitbox circular (px). El sprite se dibuja un poco más grande.
    radius: float = 22.0
    #: Tiempo (s) que tarda el pájaro en recorrer ~63 % de la distancia a su objetivo.
    #: Valores chicos = respuesta más directa; grandes = movimiento más suave.
    response_time: float = 0.07


@dataclass(frozen=True, slots=True)
class PipeConfig:
    width: float = 80.0
    #: Distancia mínima entre el hueco y el borde de la pantalla (px).
    edge_margin: float = 70.0
    #: Máximo desplazamiento vertical del hueco entre un tubo y el siguiente (px).
    max_gap_shift: float = 260.0


@dataclass(frozen=True, slots=True)
class DifficultyLevel:
    """Parámetros de un nivel. Se activa cuando el puntaje alcanza ``min_score``."""

    min_score: int
    gap: float  # alto del hueco entre tubos (px)
    speed: float  # velocidad de desplazamiento de los tubos (px/s)
    spacing: float  # distancia horizontal entre tubos consecutivos (px)


DEFAULT_DIFFICULTY: tuple[DifficultyLevel, ...] = (
    DifficultyLevel(min_score=0, gap=220, speed=300, spacing=420),
    DifficultyLevel(min_score=5, gap=210, speed=330, spacing=390),
    DifficultyLevel(min_score=10, gap=200, speed=360, spacing=360),
    DifficultyLevel(min_score=15, gap=190, speed=390, spacing=340),
    DifficultyLevel(min_score=20, gap=180, speed=420, spacing=320),
)


@dataclass(frozen=True, slots=True)
class TrackingConfig:
    camera_index: int = 0
    frame_width: int = 640
    frame_height: int = 480
    #: Espejar la imagen para que mover la cabeza a la derecha se vea a la derecha.
    mirror: bool = True
    #: Rango vertical de la imagen (0 = arriba, 1 = abajo) que se mapea a toda la
    #: pantalla. Nadie mueve la nariz hasta el borde del encuadre, así que estirar
    #: la zona cómoda hace que llegar arriba y abajo no requiera esfuerzo.
    range_top: float = 0.30
    range_bottom: float = 0.70
    #: Parámetros del filtro One Euro (suavizado adaptativo del temblor).
    filter_min_cutoff: float = 1.5
    filter_beta: float = 8.0
    #: Si la última lectura de la cámara es más vieja que esto (s), se considera perdida.
    stale_after: float = 0.5
    #: Tamaño de la vista previa de la cámara que se muestra en el juego.
    preview_size: tuple[int, int] = (192, 144)


@dataclass(frozen=True, slots=True)
class GameConfig:
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    bird: BirdConfig = field(default_factory=BirdConfig)
    pipes: PipeConfig = field(default_factory=PipeConfig)
    difficulty: tuple[DifficultyLevel, ...] = DEFAULT_DIFFICULTY
    tracking: TrackingConfig = field(default_factory=TrackingConfig)
    #: Segundos sin detectar el rostro antes de pausar el juego automáticamente.
    face_lost_grace: float = 0.25
