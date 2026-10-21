"""Ubicaciones de datos del usuario según el sistema operativo."""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR_NAME = "flappy-bird-eurekas"


def user_data_dir() -> Path:
    """Carpeta donde se guardan el récord y los modelos descargados.

    - Windows: ``%LOCALAPPDATA%\\flappy-bird-eurekas``
    - macOS: ``~/Library/Application Support/flappy-bird-eurekas``
    - Linux: ``$XDG_DATA_HOME/flappy-bird-eurekas`` (por defecto ``~/.local/share``)
    """
    if sys.platform == "win32":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / APP_DIR_NAME
