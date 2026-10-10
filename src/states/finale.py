"""Cena final: o ritual no altar, o Dragao desperta e a Sombra Cinzenta e vencida."""
import pygame

from src import config
from src.input import Action
from src.sprites import ROOT
from src.states.base import State
from src.text import draw_text, wrap

P = config.PALETTE

# (cor de fundo, linhas de texto, mostrar dragao, clarao)
PAGES = [
    ("contorno", ["As cinco princesas posicionam os quatro insumos",
                  "no altar elemental: o Barco, o Unicórnio,",
                  "o Carro Rosa e o Dragão Ancestral."], False, False),
    ("branco", ["Uma explosão de luz purificadora",
                "rasga o céu cinzento!"], False, True),
    ("roxo", ["O Dragão desperta rugindo e destrói as",
              "defesas da Sombra Cinzenta com seu sopro",
              "luminoso, desfazendo a névoa escura."], True, True),
    ("azul", ["Enquanto as quatro amigas comandam os insumos",
              "do lado de fora, Isabela entra sozinha no",
              "castelo e enfrenta o grande vilão."], False, False),
    ("vermelho_escuro", ["Espada contra espada, Isabela resiste,",
                         "avança... e vence o duelo!"], False, False),
    ("amarelo", ["O castelo pixelado é restaurado à sua forma",
                 "original, e o Reino de Cristal volta a prosperar."], False, True),
]


class Finale(State):
    def __init__(self):
        super().__init__()
        self.page = 0
        self.ticks = 0
        self.dragon = None

    def enter(self):
        sheet = pygame.image.load(str(ROOT / "assets" / "sprites" / "dragon.png")).convert_alpha()
        self.dragon = pygame.transform.scale(sheet, (96, 96))

    def update(self, dt, inp):
        self.ticks += 1
        if self.ticks > 25 and inp.pressed(Action.INTERACT):
            self.page += 1
            self.ticks = 0
            if self.page >= len(PAGES):
                from src.states.victory import Victory
                self.manager.change(Victory())

    def draw(self, canvas):
        bg, lines, dragon, flash = PAGES[min(self.page, len(PAGES) - 1)]
        canvas.fill(P[bg])
        dark_text = bg in ("branco", "amarelo")
        color = P["contorno"] if dark_text else P["branco"]
        if dragon and self.dragon:
            bob = int(4 * pygame.math.Vector2(0, 1).rotate(self.ticks * 6).y)
            canvas.blit(self.dragon, ((config.LOGICAL_W - 96) // 2, 10 + bob))
        top = 112 if dragon else 56
        for i, line in enumerate(lines):
            draw_text(canvas, line, config.LOGICAL_W // 2, top + i * 15, color, size=16, center=True)
        if flash and self.ticks < 18:
            glow = pygame.Surface((config.LOGICAL_W, config.LOGICAL_H), pygame.SRCALPHA)
            glow.fill((*P["branco"], 220 - self.ticks * 12))
            canvas.blit(glow, (0, 0))
        if (self.ticks // 30) % 2 == 0 and self.ticks > 25:
            draw_text(canvas, "Aperte Z", config.LOGICAL_W // 2, 160, color, size=14, center=True)
