"""Estado Titulo: nome do jogo e 'iniciar'."""
from src import config
from src.input import Action
from src.states.base import State
from src.states.play import Play
from src.text import draw_text

BLINK_TICKS = 30


class Title(State):
    def __init__(self):
        super().__init__()
        self.ticks = 0

    def update(self, dt, inp):
        self.ticks += 1
        if inp.pressed(Action.INTERACT):
            self.manager.change(Play())

    def draw(self, canvas):
        p = config.PALETTE
        canvas.fill(p["folha_escura"])
        cx = config.LOGICAL_W // 2
        draw_text(canvas, "A JORNADA DA BELA", cx, 60, p["creme"], size=28, center=True)
        if (self.ticks // BLINK_TICKS) % 2 == 0:
            draw_text(canvas, "Aperte Z para iniciar", cx, 120, p["amarelo_brilho"], size=16, center=True)
