"""Estado Titulo: tela inicial rosa com o nome do jogo e petalas flutuando."""
import math
import random

import pygame

from src import config
from src.input import Action
from src.sprites import character
from src.states.base import State
from src.states.cutscene import Cutscene
from src.text import draw_text

BLINK_TICKS = 30
P = config.PALETTE


class Title(State):
    def __init__(self):
        super().__init__()
        self.ticks = 0
        rng = random.Random(21)
        # petalas: [x, y, velocidade de queda, fase do balanco, cor]
        self.petals = [
            [rng.uniform(0, config.LOGICAL_W), rng.uniform(0, config.LOGICAL_H),
             rng.uniform(0.25, 0.7), rng.uniform(0, math.tau),
             rng.choice(("branco", "areia_clara", "rosa_escuro", "branco"))]
            for _ in range(26)
        ]

    def update(self, dt, inp):
        self.ticks += 1
        for pt in self.petals:
            pt[1] += pt[2]
            if pt[1] > config.LOGICAL_H + 4:
                pt[1] = -4
        if inp.pressed(Action.INTERACT):
            self.manager.change(Cutscene("intro"))

    def draw(self, canvas):
        H = config.LOGICAL_H
        # fundo rosa em faixas suaves (claro em cima, mais forte embaixo)
        bands = ("rosa", "rosa", "rosa", "rosa", "rosa_escuro")
        h = H // 6 + 1
        canvas.fill(P["rosa"])
        pygame.draw.rect(canvas, P["rosa_escuro"], (0, H - h, config.LOGICAL_W, h))
        pygame.draw.rect(canvas, P["rosa"], (0, 0, config.LOGICAL_W, h))
        for x in range(0, config.LOGICAL_W, 8):                    # barra de coracoes/pontos na borda de baixo
            canvas.fill(P["rosa"], (x + 2, H - h + 3, 3, 2))
        for x, y, _s, ph, color in self.petals:
            sx = int(x + math.sin(self.ticks / 30.0 + ph) * 6)
            canvas.fill(P[color], (sx, int(y), 2, 2))
            canvas.fill(P[color], (sx + 1, int(y) + 1, 2, 1))
        cx = config.LOGICAL_W // 2
        # titulo branco com sombra rosa-escura
        draw_text(canvas, "A JORNADA DA BELA", cx, 42, P["branco"], size=28, center=True, shadow=P["rosa_escuro"])
        # a Isabela, sorridente, sobre a faixa de baixo
        frame = character("isabela")["down"][0]
        big = pygame.transform.scale(frame, (frame.get_width() * 2, frame.get_height() * 2))
        bob = 1 if (self.ticks // 40) % 2 else 0
        canvas.blit(big, (cx - big.get_width() // 2, H - h - big.get_height() + 8 - bob))
        if (self.ticks // BLINK_TICKS) % 2 == 0:
            draw_text(canvas, "Aperte Z para iniciar", cx, 82, P["vermelho_escuro"], size=16, center=True)
