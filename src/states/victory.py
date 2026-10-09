"""Estado Vitoria: a Bela chegou ao castelo."""
from src import config
from src.input import Action
from src.states.base import State
from src.text import draw_text


class Victory(State):
    def __init__(self):
        super().__init__()
        self.ticks = 0

    def update(self, dt, inp):
        self.ticks += 1
        if self.ticks > 30 and inp.pressed(Action.INTERACT):  # evita pular sem querer
            from src.states.title import Title  # import local: evita ciclo
            self.manager.change(Title())

    def draw(self, canvas):
        p = config.PALETTE
        canvas.fill(p["lilas_magia"])
        cx = config.LOGICAL_W // 2
        draw_text(canvas, "VITÓRIA!", cx, 50, p["creme"], size=36, center=True)
        draw_text(canvas, "Bela chegou ao castelo.", cx, 95, p["contorno"], size=18, center=True)
        if (self.ticks // 30) % 2 == 0:
            draw_text(canvas, "Aperte Z para continuar", cx, 130, p["creme"], size=16, center=True)
