"""Texto do jogo com a fonte pixel Jersey 15 (SIL Open Font License; ver assets/fonts/OFL.txt).

Os tamanhos pedidos pelo codigo (12..40) sao mapeados para 3 tamanhos nitidos da fonte:
16 (texto comum, tamanho nativo), 32 (titulos) e 48 (destaques), sempre multiplos do nativo.
"""
import pygame

from src.sprites import ROOT

FONT_PATH = ROOT / "assets" / "fonts" / "Jersey15-Regular.ttf"
_fonts = {}


def _resolve(size):
    if size <= 17:
        return 16
    if size <= 30:
        return 32
    return 48


def get_font(size):
    px = _resolve(size)
    font = _fonts.get(px)
    if font is None:
        try:
            font = pygame.font.Font(str(FONT_PATH), px)
        except Exception:               # sem a fonte, usa a padrao do pygame
            font = pygame.font.Font(None, size)
        _fonts[px] = font
    return font


def line_height(size):
    return get_font(size).get_height()


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
