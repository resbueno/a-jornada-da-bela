"""Pecas simples de interface: painel com moldura dupla e menu vertical."""
import pygame

from src import config
from src.text import draw_text


def draw_panel(canvas, rect):
    p = config.PALETTE
    x, y, w, h = rect
    pygame.draw.rect(canvas, p["contorno"], rect, border_radius=6)
    pygame.draw.rect(canvas, p["creme"], (x + 3, y + 3, w - 6, h - 6), 2, border_radius=4)
    pygame.draw.rect(canvas, p["rosa_escuro"], (x + 6, y + 6, w - 12, h - 12), 1, border_radius=3)


def draw_menu(canvas, rect, title, entries, cursor, footer=None):
    """Painel com titulo e lista vertical; `cursor` e o indice destacado."""
    p = config.PALETTE
    draw_panel(canvas, rect)
    x, y, w, h = rect
    draw_text(canvas, title, x + w // 2, y + 10, p["amarelo_brilho"], size=32, center=True)
    for i, text in enumerate(entries):
        color = p["creme"] if i == cursor else p["pedra_clara"]
        prefix = "> " if i == cursor else "  "
        draw_text(canvas, prefix + text, x + 20, y + 50 + i * 32, color, size=32)
    if footer:
        draw_text(canvas, footer, x + w // 2, y + h - 30, p["rosa"], size=16, center=True)
