"""Estado Vitoria: as amigas chegaram ao banquete a tempo."""
from src import config
from src.input import Action
from src.sprites import character
from src.states.base import State
from src.text import draw_text

P = config.PALETTE
W, H = config.LOGICAL_W, config.LOGICAL_H


class Victory(State):
    def __init__(self):
        super().__init__()
        self.ticks = 0

    def update(self, dt, inp):
        self.ticks += 1
        if self.ticks > 40 and inp.pressed(Action.INTERACT):  # evita pular sem querer
            from src.states.title import Title  # import local: evita ciclo
            self.manager.change(Title())

    def draw(self, canvas):
        canvas.fill(P["roxo"])
        for k in range(40):                                   # confete
            x = (k * 97 + self.ticks * (1 + k % 3)) % W
            y = (k * 53 + self.ticks * (2 + k % 4)) % H
            canvas.fill(P[("rosa", "amarelo", "branco", "ceu", "verde_brilho")[k % 5]], (x, y, 4, 4))
        draw_text(canvas, "FIM", W // 2, 20, P["areia_clara"], size=96, center=True)
        draw_text(canvas, "A Jornada da Bela", W // 2, 124, P["contorno"], size=32, center=True)
        draw_text(canvas, "Bela, Lana, Lara e Olívia chegaram a tempo do jantar!", W // 2, 160, P["branco"],
                  size=32, center=True, shadow=P["contorno"])
        for i, name in enumerate(("lana_gala", "isabela_gala", "lara_gala", "olivia_gala")):
            frame = character(name)["down"][0]
            hop = 8 if ((self.ticks + i * 9) // 14) % 2 else 0
            canvas.blit(frame, (W // 2 - 76 + i * 40, 224 - hop))
        if (self.ticks // 30) % 2 == 0:
            draw_text(canvas, "Aperte Z para jogar de novo", W // 2, 300, P["areia_clara"], size=32, center=True)
