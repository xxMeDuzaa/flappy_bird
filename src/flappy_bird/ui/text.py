"""Normalización del texto que se muestra en pantalla (sin dependencias de pygame).

La fuente por defecto de pygame dibuja mal las letras acentuadas, así que todo
texto visible pasa por :func:`plain_text` antes de renderizarse: quita tildes y
diéresis, cambia la ñ por n y elimina signos que la fuente no soporta.
"""

from __future__ import annotations

import unicodedata

_REPLACEMENTS = str.maketrans({"¡": "", "¿": "", "·": "-", "–": "-", "—": "-", "“": '"', "”": '"'})


def plain_text(text: str) -> str:
    """Devuelve ``text`` sólo con caracteres ASCII (``"¡Récord!"`` → ``"Record!"``)."""
    decomposed = unicodedata.normalize("NFKD", text.translate(_REPLACEMENTS))
    without_marks = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return without_marks.encode("ascii", "ignore").decode("ascii")
