"""Estado Pausa: continuar ou voltar ao titulo."""
from src import config
from src.input import Action
from src.states.base import State
from src.ui import draw_menu

ENTRIES = ["Continuar", "Sair para o título"]


class Pause(State):
    overlay = True

    def __init__(self):
        super().__init__()
        self.cursor = 0

    def update(self, dt, inp):
        if inp.pressed(Action.PAUSE):
            self.manager.pop()
        elif inp.pressed(Action.UP):
            self.cursor = (self.cursor - 1) % len(ENTRIES)
        elif inp.pressed(Action.DOWN):
            self.cursor = (self.cursor + 1) % len(ENTRIES)
        elif inp.pressed(Action.INTERACT):
            if self.cursor == 0:
                self.manager.pop()
            else:
                from src.states.title import Title  # import local: evita ciclo Title <-> Play <-> Pause
                self.manager.change(Title())

    def draw(self, canvas):
        w, h = 170, 30 + len(ENTRIES) * 14 + 10
        rect = ((config.LOGICAL_W - w) // 2, (config.LOGICAL_H - h) // 2, w, h)
        draw_menu(canvas, rect, "PAUSA", ENTRIES, self.cursor)
