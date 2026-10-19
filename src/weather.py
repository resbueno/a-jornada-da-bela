"""Clima: chuva em gotas diagonais e vento com riscos e folhinhas (deterministico)."""
import math
import random

import pygame

from src import config

P = config.PALETTE
W, H = config.LOGICAL_W, config.LOGICAL_H


class Rain:
    def __init__(self, count=220, seed=11):
        rng = random.Random(seed)
        self.calm = 110             # gotas usadas com tempo calmo
        self.heavy = False
        self.drops = [
            [rng.uniform(0, W + 80), rng.uniform(0, H), rng.uniform(4.4, 6.8), rng.choice((6, 8, 10)),
             rng.random() < 0.25]
            for _ in range(count)
        ]
        self.tint = pygame.Surface((W, H), pygame.SRCALPHA)
        self.tint.fill((*P["agua_escura"], 26))

    def update(self):
        for d in self.drops:
            d[0] -= d[2] * 0.45     # inclinacao para a esquerda
            d[1] += d[2]
            if d[1] > H + 12 or d[0] < -12:
                d[1] = -12
                d[0] += W * 0.8

    def draw(self, canvas):
        canvas.blit(self.tint, (0, 0))
        for x, y, _speed, length, bright in self.drops[: len(self.drops) if self.heavy else self.calm]:
            color = P["branco"] if bright else P["ceu"]
            pygame.draw.line(canvas, color, (int(x), int(y)), (int(x) + length // 2, int(y) - length))


class Wind:
    """Rajadas: riscos brancos atravessando a tela da esquerda para a direita e folhinhas girando."""

    def __init__(self, seed=5):
        rng = random.Random(seed)
        self.ticks = 0
        self.streaks = [[rng.uniform(0, W), rng.uniform(0, H), rng.uniform(7, 13), rng.randint(20, 46)]
                        for _ in range(26)]
        self.leaves = [[rng.uniform(0, W), rng.uniform(0, H), rng.uniform(3, 6), rng.uniform(0, 6.3),
                        rng.choice(("verde_claro", "laranja", "amarelo", "branco"))] for _ in range(14)]

    def update(self):
        self.ticks += 1
        for s in self.streaks:
            s[0] += s[2]
            if s[0] > W + 50:
                s[0] = -s[3]
        for leaf in self.leaves:
            leaf[0] += leaf[2]
            leaf[1] += math.sin(self.ticks / 10.0 + leaf[3]) * 1.2
            if leaf[0] > W + 8:
                leaf[0] = -8

    def draw(self, canvas):
        for x, y, _v, length in self.streaks:
            wave = int(math.sin((x + self.ticks) / 30.0) * 2)
            pygame.draw.line(canvas, P["branco"], (int(x), int(y) + wave), (int(x) + length, int(y) + wave))
        for x, y, _v, ph, color in self.leaves:
            k = (self.ticks // 6 + int(ph)) % 2
            canvas.fill(P[color], (int(x), int(y), 4 if k else 2, 2 if k else 4))
