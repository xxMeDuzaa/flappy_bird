import pytest

from flappy_bird.ui.text import plain_text


@pytest.mark.parametrize(
    ("original", "expected"),
    [
        ("¡NUEVO RÉCORD!", "NUEVO RECORD!"),
        ("Cámara (MediaPipe)", "Camara (MediaPipe)"),
        ("pájaro · niño · pingüino", "pajaro - nino - pinguino"),
        ("¿Listo?", "Listo?"),
        ("Score: 12", "Score: 12"),
    ],
)
def test_plain_text_removes_accents(original: str, expected: str) -> None:
    assert plain_text(original) == expected
    assert plain_text(original).isascii()
