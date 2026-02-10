import os
import pygame

_font_cache = {}

_FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "fonts")

_FONT_FILES = {
    (False, False): "EBGaramond-Regular.ttf",
    (True, False):  "EBGaramond-Bold.ttf",
    (False, True):  "EBGaramond-Italic.ttf",
    (True, True):   "EBGaramond-BoldItalic.ttf",
}


def get_font(size, bold=False, italic=False):
    """Return a cached pygame.font.Font for the given size and style."""
    key = (size, bold, italic)
    if key not in _font_cache:
        filename = _FONT_FILES.get((bold, italic), "EBGaramond-Regular.ttf")
        path = os.path.join(_FONT_DIR, filename)
        try:
            font = pygame.font.Font(path, size)
        except FileNotFoundError:
            fallback = os.path.join(_FONT_DIR, "EBGaramond-Regular.ttf")
            font = pygame.font.Font(fallback, size)
        _font_cache[key] = font
    return _font_cache[key]
