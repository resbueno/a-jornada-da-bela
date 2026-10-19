"""Escuridao e neblina com luzes circulares (lanterna da Bela, lampioes, vaga-lumes) e tons de hora do dia.

A luz e feita em degraus (estilo pixel art): circulos concentricos cada vez mais transparentes.
"""
import pygame

from src import config

LEVELS = 6  # degraus de brilho
NIGHT = (8, 10, 30)
FOG = (200, 214, 226)


class Darkness:
    def __init__(self, alpha=214, color=NIGHT):
        self.alpha = alpha
        self.color = color
        self.layer = pygame.Surface((config.LOGICAL_W, config.LOGICAL_H), pygame.SRCALPHA)
        self._holes = {}

    def _hole(self, r):
        r = max(4, int(r) // 2 * 2)
        h = self._holes.get(r)
        if h is None:
            h = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
            h.fill((*self.color, self.alpha))
            for step in range(LEVELS - 1, -1, -1):           # de fora para dentro, cada vez mais claro
                a = int(self.alpha * (step / LEVELS) ** 1.6)
                rr = round(r * (step + 1) / LEVELS)
                pygame.draw.circle(h, (*self.color, a), (r, r), rr)
            self._holes[r] = h
        return h

    def draw(self, canvas, lights, ticks=0, strength=1.0):
        """`lights`: [(x_tela, y_tela, raio)]. `strength` 0..1 apaga o efeito aos poucos."""
        if strength <= 0:
            return
        self.layer.fill((*self.color, self.alpha))
        for x, y, r in lights:
            hole = self._hole(r)
            self.layer.blit(hole, (int(x) - hole.get_width() // 2, int(y) - hole.get_height() // 2),
                            special_flags=pygame.BLEND_RGBA_MIN)
        self.layer.set_alpha(int(255 * min(strength, 1.0)))
        canvas.blit(self.layer, (0, 0))


TINTS = {
    "tarde": [("amarelo", 14), ("areia_clara", 10), ("amarelo", 12)],
    "entardecer": [("laranja", 22), ("amarelo", 18), ("laranja", 24)],
    "por_do_sol": [("rosa_escuro", 34), ("laranja", 30), ("amarelo", 22), ("laranja", 30), ("rosa_escuro", 38)],
}


class Tint:
    """Tom da hora do dia sobre a cena: faixas de cor bem suaves (o sol vai baixando na jornada)."""

    def __init__(self, name):
        from src.config import PALETTE as P

        self.layer = pygame.Surface((config.LOGICAL_W, config.LOGICAL_H), pygame.SRCALPHA)
        bands = TINTS[name]
        h = config.LOGICAL_H // len(bands) + 1
        for i, (color, alpha) in enumerate(bands):
            pygame.draw.rect(self.layer, (*P[color], alpha), (0, i * h, config.LOGICAL_W, h))

    def draw(self, canvas):
        canvas.blit(self.layer, (0, 0))
