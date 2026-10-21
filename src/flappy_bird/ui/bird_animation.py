"""Animación de las alas según la dirección del vuelo (sin dependencias de pygame).

- **Subiendo**: aletea rápido y con mucha amplitud, como haciendo fuerza.
- **Estable**: aleteo tranquilo.
- **Bajando**: deja de aletear y sostiene las alas levantadas, planeando.

Las transiciones entre estos modos son continuas: la "intención" de subir o bajar
se suaviza en el tiempo para que el ala nunca salte de una pose a otra.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WingStyle:
    frequency: float  # aleteos por segundo
    amplitude: float  # grados hacia arriba y abajo de la pose base
    offset: float  # pose base en grados (positivo = ala levantada)


CRUISE = WingStyle(frequency=4.0, amplitude=26.0, offset=0.0)
CLIMB = WingStyle(frequency=8.0, amplitude=42.0, offset=-5.0)
GLIDE = WingStyle(frequency=1.5, amplitude=5.0, offset=32.0)

#: Velocidad vertical (px/s) a partir de la cual se considera subida/caída plena.
FULL_EFFECT_SPEED = 500.0
#: Constante de tiempo (s) con la que se suaviza el cambio de modo.
BLEND_TIME = 0.12


def _mix(a: WingStyle, b: WingStyle, t: float) -> WingStyle:
    return WingStyle(
        frequency=a.frequency + (b.frequency - a.frequency) * t,
        amplitude=a.amplitude + (b.amplitude - a.amplitude) * t,
        offset=a.offset + (b.offset - a.offset) * t,
    )


class WingAnimator:
    def __init__(self) -> None:
        self._phase = 0.0
        #: -1 = subiendo a fondo, 0 = estable, +1 = cayendo a fondo.
        self._intent = 0.0
        self.angle = 0.0

    @property
    def intent(self) -> float:
        return self._intent

    def update(self, dt: float, velocity_y: float) -> float:
        """Avanza la animación y devuelve el ángulo del ala en grados."""
        if dt <= 0:
            return self.angle

        target = max(-1.0, min(1.0, velocity_y / FULL_EFFECT_SPEED))
        self._intent += (target - self._intent) * (1.0 - math.exp(-dt / BLEND_TIME))

        if self._intent < 0:
            style = _mix(CRUISE, CLIMB, -self._intent)
        else:
            style = _mix(CRUISE, GLIDE, self._intent)

        # Se avanza la fase (no el tiempo) para que cambiar la frecuencia no haga saltar el ala.
        self._phase = (self._phase + math.tau * style.frequency * dt) % math.tau
        self.angle = style.offset + style.amplitude * math.sin(self._phase)
        return self.angle
