"""Estado Fim de capitulo: aparece ao chegar na entrada da caverna."""
from src import config
from src.input import Action
from src.states.base import State
from src.text import draw_text


class ChapterEnd(State):
    def __init__(self, title, lines):
        super().__init__()
        self.title = title
        self.lines = lines
        self.ticks = 0

    def update(self, dt, inp):
        self.ticks += 1
        if self.ticks > 30 and inp.pressed(Action.INTERACT):
            from src.states.title import Title  # import local: evita ciclo
            self.manager.change(Title())

    def draw(self, canvas):
        p = config.PALETTE
        canvas.fill(p["contorno"])
        cx = config.LOGICAL_W // 2
        draw_text(canvas, self.title, cx, 36, p["amarelo"], size=26, center=True)
        for i, line in enumerate(self.lines):
            draw_text(canvas, line, cx, 76 + i * 15, p["areia_clara"], size=16, center=True)
        if (self.ticks // 30) % 2 == 0:
            draw_text(canvas, "Aperte Z para voltar ao título", cx, 150, p["rosa"], size=14, center=True)
