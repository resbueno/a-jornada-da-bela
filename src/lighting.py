"""Escuridao com luzes circulares (cristais, Isabela). Sombra em degraus, no estilo pixel art."""
import math

import pygame

from src import config

AMBIENT = (8, 10, 30)
LEVELS = 6  # degraus de brilho


class Darkness:
    def __init__(self, alpha=214):
        self.alpha = alpha
        self.layer = pygame.Surface((config.LOGICAL_W, config.LOGICAL_H), pygame.SRCALPHA)
        self._holes = {}

    def _hole(self, r):
        h = self._holes.get(r)
        if h is None:
            h = pygame.Surface((2 * r, 2 * r), pygame.SRCALPHA)
            for y in range(2 * r):
                for x in range(2 * r):
                    d = math.hypot(x - r + 0.5, y - r + 0.5) / r
                    if d >= 1:
                        a = self.alpha
                    else:
                        step = int(d * LEVELS)                      # 0..LEVELS-1
                        a = int(self.alpha * (step / LEVELS) ** 1.6)
                    h.set_at((x, y), (*AMBIENT, a))
            self._holes[r] = h
        return h

    def draw(self, canvas, lights, ticks):
        """`lights`: [(x_tela, y_tela, raio, tremula)]."""
        self.layer.fill((*AMBIENT, self.alpha))
        for x, y, r, flicker in lights:
            rr = r + (int(math.sin(ticks / 9.0 + x) * 2) if flicker else 0)
            self.layer.blit(self._hole(rr), (int(x) - rr, int(y) - rr), special_flags=pygame.BLEND_RGBA_MIN)
        canvas.blit(self.layer, (0, 0))
