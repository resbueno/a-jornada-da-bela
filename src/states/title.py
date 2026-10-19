"""Estado Titulo: a paisagem com o castelo no alto da montanha, o nome do jogo e as quatro amigas."""
import pygame

from src import config
from src.input import Action
from src.scenery import draw_panorama
from src.sprites import character
from src.states.base import State
from src.text import draw_text

BLINK_TICKS = 30
P = config.PALETTE
W, H = config.LOGICAL_W, config.LOGICAL_H


class Title(State):
    def __init__(self):
        super().__init__()
        self.ticks = 0

    def update(self, dt, inp):
        self.ticks += 1
        if inp.pressed(Action.INTERACT):
            from src.states.cutscene import Cutscene
            self.manager.change(Cutscene("intro"))

    def draw(self, canvas):
        draw_panorama(canvas, "tarde", self.ticks)
        cx = 210
        for text, y in (("A JORNADA", 14), ("DA BELA", 70)):
            draw_text(canvas, text, cx + 4, y + 4, P["rosa_escuro"], size=64, center=True)
            draw_text(canvas, text, cx, y, P["branco"], size=64, center=True)
        draw_text(canvas, "De volta ao castelo a tempo do jantar!", cx, 140, P["contorno"], size=16, center=True)
        for i, name in enumerate(("lana", "isabela", "lara", "olivia")):
            frame = character(name)["down"][0]
            big = pygame.transform.scale(frame, (frame.get_width() * 2, frame.get_height() * 2))
            bob = 3 if ((self.ticks + i * 12) // 24) % 2 else 0
            x = W // 2 - 150 + i * 76
            canvas.blit(big, (x, H - big.get_height() - 4 - bob))
        if (self.ticks // BLINK_TICKS) % 2 == 0:
            draw_text(canvas, "Aperte Z para começar", cx, 166, P["branco"], size=32, center=True, shadow=P["contorno"])
