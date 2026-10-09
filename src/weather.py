"""Clima: chuva em gotas diagonais com leve tom frio sobre a cena (deterministico)."""
import random

import pygame

from src import config

P = config.PALETTE


class Rain:
    def __init__(self, count=140, seed=11):
        rng = random.Random(seed)
        self.calm = 60              # gotas usadas com tempo calmo
        self.storm = False
        self.flash = 0
        self.ticks = 0
        self.drops = [
            [rng.uniform(0, config.LOGICAL_W + 40), rng.uniform(0, config.LOGICAL_H),
             rng.uniform(2.2, 3.4), rng.choice((3, 4, 5)), rng.random() < 0.25]
            for _ in range(count)
        ]
        self.tint = pygame.Surface((config.LOGICAL_W, config.LOGICAL_H), pygame.SRCALPHA)
        self.tint.fill((*P["agua_escura"], 26))

    def update(self):
        self.ticks += 1
        if self.flash:
            self.flash -= 1
        elif self.storm and self.ticks % 360 == 200:
            self.flash = 9                      # relampago
        for d in self.drops:
            d[0] -= d[2] * 0.45   # inclinacao para a esquerda
            d[1] += d[2]
            if d[1] > config.LOGICAL_H + 6 or d[0] < -6:
                d[1] = -6
                d[0] += config.LOGICAL_W * 0.8

    def draw(self, canvas):
        canvas.blit(self.tint, (0, 0))
        if self.storm:
            canvas.blit(self.tint, (0, 0))      # mais escuro na tempestade
        for x, y, _speed, length, bright in self.drops[: len(self.drops) if self.storm else self.calm]:
            color = P["branco"] if bright else P["ceu"]
            for k in range(length):
                px = int(x) + k // 2
                py = int(y) - k
                if 0 <= px < config.LOGICAL_W and 0 <= py < config.LOGICAL_H:
                    canvas.set_at((px, py), color)
        if self.flash:
            glow = pygame.Surface((config.LOGICAL_W, config.LOGICAL_H), pygame.SRCALPHA)
            glow.fill((*P["branco"], 18 * self.flash))
            canvas.blit(glow, (0, 0))
