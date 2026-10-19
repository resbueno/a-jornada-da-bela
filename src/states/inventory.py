"""Estado Inventario: transportes (troca so em terreno compativel), amigas do grupo e itens."""
from src import config
from src.input import Action
from src.inventory import FRIEND_NAMES
from src.states.base import State
from src.text import draw_text
from src.ui import draw_menu

MESSAGE_TICKS = 120
P = config.PALETTE


class InventoryState(State):
    overlay = True

    def __init__(self, play):
        super().__init__()
        self.play = play
        self.items = play.inventory.transports
        self.cursor = self.items.index(play.player.transport) if play.player.transport in self.items else 0
        self.message = ""
        self.message_ticks = 0

    def update(self, dt, inp):
        if self.message_ticks:
            self.message_ticks -= 1
            if not self.message_ticks:
                self.message = ""
        if inp.pressed(Action.INVENTORY) or inp.pressed(Action.PAUSE):
            self.manager.pop()
        elif inp.pressed(Action.UP):
            self.cursor = (self.cursor - 1) % len(self.items)
        elif inp.pressed(Action.DOWN):
            self.cursor = (self.cursor + 1) % len(self.items)
        elif inp.pressed(Action.INTERACT):
            self._choose(self.items[self.cursor])

    def _choose(self, transport):
        player = self.play.player
        if transport is player.transport:
            self.manager.pop()
        elif player.switch_transport(transport, self.play.world):
            self.play.trail.reset(player.x, player.y)
            self.manager.pop()
        else:
            self.message = f"{transport.name} não serve aqui."
            self.message_ticks = MESSAGE_TICKS

    def draw(self, canvas):
        inv = self.play.inventory
        current = self.play.player.transport
        entries = [t.name + ("  (em uso)" if t is current else "") for t in self.items]
        w = 420
        h = 60 + len(entries) * 32 + 110
        rect = ((config.LOGICAL_W - w) // 2, (config.LOGICAL_H - h) // 2, w, h)
        draw_menu(canvas, rect, "MOCHILA", entries, self.cursor, footer=self.message or "Z escolhe   I fecha")
        x, y = rect[0] + 24, rect[1] + 56 + len(entries) * 32 + 8
        friends = ", ".join(FRIEND_NAMES[f] for f in inv.friends) or "ninguém ainda"
        draw_text(canvas, "Amigas: " + friends, x, y, P["areia_clara"], size=16)
        items = ", ".join(inv.items()) or "nada ainda"
        draw_text(canvas, "Itens: " + items, x, y + 22, P["areia_clara"], size=16)
