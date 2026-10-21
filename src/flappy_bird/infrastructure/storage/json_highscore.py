"""Persistencia del récord en un archivo JSON."""

from __future__ import annotations

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class JsonHighScoreRepository:
    """Guarda el récord en ``{"high_score": N}``.

    La escritura es atómica (archivo temporal + reemplazo) para que un cierre
    inesperado nunca deje el archivo corrupto.
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    def load(self) -> int:
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            return 0
        except (OSError, json.JSONDecodeError) as error:
            logger.warning("No se pudo leer el récord en %s: %s", self._path, error)
            return 0

        value = data.get("high_score", 0) if isinstance(data, dict) else 0
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            logger.warning("Récord inválido en %s; se reinicia a 0", self._path)
            return 0
        return value

    def save(self, score: int) -> None:
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self._path.with_suffix(".tmp")
            tmp.write_text(json.dumps({"high_score": score}), encoding="utf-8")
            tmp.replace(self._path)
        except OSError as error:
            logger.error("No se pudo guardar el récord en %s: %s", self._path, error)
