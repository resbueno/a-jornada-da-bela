"""Estado Dialogo: caixa embaixo, texto letra por letra; interagir completa ou avanca."""
import pygame

from src import config
from src.input import Action
from src.states.base import State
from src.text import draw_text, wrap
from src.ui import draw_panel

BOX = (4, config.LOGICAL_H - 76, config.LOGICAL_W - 8, 72)
TEXT_SIZE = 16
LINE_H = 16
MAX_LINES = 3
CHARS_PER_TICK = 0.6  # ~36 letras por segundo a 60 Hz


class DialogueState(State):
    overlay = True

    def __init__(self, speaker, messages, on_finish=None):
        super().__init__()
        self.speaker = speaker
        self.on_finish = on_finish
        width = BOX[2] - 16
        self.pages = []
        for message in messages:
            lines = wrap(message, TEXT_SIZE, width)
            for i in range(0, len(lines), MAX_LINES):
                self.pages.append(lines[i:i + MAX_LINES])
        self.page = 0
        self.revealed = 0.0
        self.ticks = 0

    @property
    def _total(self):
        return sum(len(line) for line in self.pages[self.page])

    @property
    def _complete(self):
        return self.revealed >= self._total

    def update(self, dt, inp):
        self.ticks += 1
        if not self._complete:
            self.revealed = min(self.revealed + CHARS_PER_TICK, self._total)
        if inp.pressed(Action.INTERACT):
            if not self._complete:
                self.revealed = self._total          # completa a frase na hora
            elif self.page + 1 < len(self.pages):
                self.page += 1
                self.revealed = 0.0
            else:
                self.manager.pop()
                if self.on_finish:
                    self.on_finish()

    def draw(self, canvas):
        p = config.PALETTE
        draw_panel(canvas, BOX)
        x, y = BOX[0] + 8, BOX[1] + 5
        if self.speaker:
            draw_text(canvas, self.speaker, x, y, p["amarelo_brilho"], size=TEXT_SIZE)
            y += LINE_H
        remaining = int(self.revealed)
        for line in self.pages[self.page]:
            shown = line[:remaining]
            remaining -= len(line)
            draw_text(canvas, shown, x, y, p["creme"], size=TEXT_SIZE)
            y += LINE_H
            if remaining <= 0:
                break
        if self._complete and (self.ticks // 20) % 2 == 0:
            bx, by = BOX[0] + BOX[2] - 14, BOX[1] + BOX[3] - 10
            pygame.draw.polygon(canvas, p["rosa"], [(bx, by), (bx + 6, by), (bx + 3, by + 4)])
