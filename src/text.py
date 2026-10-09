"""Texto provisorio com a fonte padrao do pygame, sem suavizacao.

Sera substituido por uma fonte pixel propria quando a arte final da UI existir.
"""
import pygame

_fonts = {}


def get_font(size):
    font = _fonts.get(size)
    if font is None:
        font = _fonts[size] = pygame.font.Font(None, size)
    return font


def draw_text(canvas, text, x, y, color, size=16, center=False, shadow=None):
    """`shadow`: cor opcional de uma sombra de 1 px (melhora o contraste sobre o mapa)."""
    font = get_font(size)
    surf = font.render(text, False, color)
    if center:
        x = x - surf.get_width() // 2
    if shadow is not None:
        canvas.blit(font.render(text, False, shadow), (x + 1, y + 1))
    canvas.blit(surf, (x, y))


def wrap(text, size, max_width):
    """Quebra `text` em linhas que cabem em `max_width` pixels."""
    font = get_font(size)
    lines, current = [], ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if font.size(trial)[0] <= max_width or not current:
            current = trial
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
