import string

from flappy_bird.ui.glyphs import (
    _RAW,
    GLYPH_HEIGHT,
    GLYPH_WIDTH,
    GLYPHS,
    LETTER_SPACING,
    text_pixels,
    text_size,
)


def test_every_glyph_is_a_5x7_grid() -> None:
    for char, rows in _RAW.items():
        lines = rows.split()
        assert len(lines) == GLYPH_HEIGHT, char
        assert all(len(line) == GLYPH_WIDTH and set(line) <= {"#", "."} for line in lines), char


def test_font_covers_letters_digits_and_punctuation() -> None:
    needed = set(string.ascii_uppercase + string.digits + " .,:!?()-|/'")
    assert needed <= GLYPHS.keys()


def test_glyphs_are_distinct() -> None:
    visible = [g for c, g in GLYPHS.items() if c != " "]
    assert len(set(visible)) == len(visible)


def test_text_size() -> None:
    advance = GLYPH_WIDTH + LETTER_SPACING
    assert text_size("") == (0, GLYPH_HEIGHT)
    assert text_size("AB") == (2 * advance - LETTER_SPACING, GLYPH_HEIGHT)


def test_text_pixels_are_uppercase_and_offset() -> None:
    advance = GLYPH_WIDTH + LETTER_SPACING
    pixels = text_pixels("ia")
    first = {p for p in pixels if p[0] < advance}
    second = {(x - advance, y) for x, y in pixels if x >= advance}
    assert first == GLYPHS["I"]
    assert second == GLYPHS["A"]


def test_unknown_characters_fall_back_to_question_mark() -> None:
    assert set(text_pixels("@")) == GLYPHS["?"]
