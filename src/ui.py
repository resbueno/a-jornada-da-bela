"""Pecas simples de interface (provisorias, com texto da fonte padrao)."""
import pygame

from src import config
from src.text import draw_text


def draw_panel(canvas, rect):
    p = config.PALETTE
    pygame.draw.rect(canvas, p["contorno"], rect)
    pygame.draw.rect(canvas, p["creme"], rect, 1)


def draw_menu(canvas, rect, title, entries, cursor, footer=None):
    """Painel com titulo e lista vertical; `cursor` e o indice destacado."""
    p = config.PALETTE
    draw_panel(canvas, rect)
    x, y, w, h = rect
    draw_text(canvas, title, x + w // 2, y + 6, p["amarelo_brilho"], size=16, center=True)
    for i, text in enumerate(entries):
        color = p["creme"] if i == cursor else p["pedra_clara"]
        prefix = "> " if i == cursor else "  "
        draw_text(canvas, prefix + text, x + 10, y + 27 + i * 17, color, size=16)
    if footer:
        draw_text(canvas, footer, x + w // 2, y + h - 18, p["rosa"], size=14, center=True)
