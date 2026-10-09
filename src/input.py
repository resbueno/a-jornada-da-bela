"""Entrada: teclado (e, depois, toque) convertida em acoes abstratas.

O jogo nunca le teclas diretamente; consulta Action. O toque (componente 10)
usa press()/release() com sua propria fonte, sem mexer no resto.
"""
from enum import Enum

import pygame


class Action(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    INTERACT = "interact"
    INVENTORY = "inventory"
    PAUSE = "pause"


DIRECTION_VECTORS = {
    Action.UP: (0, -1),
    Action.DOWN: (0, 1),
    Action.LEFT: (-1, 0),
    Action.RIGHT: (1, 0),
}

KEY_MAP = {
    pygame.K_UP: Action.UP,
    pygame.K_w: Action.UP,
    pygame.K_DOWN: Action.DOWN,
    pygame.K_s: Action.DOWN,
    pygame.K_LEFT: Action.LEFT,
    pygame.K_a: Action.LEFT,
    pygame.K_RIGHT: Action.RIGHT,
    pygame.K_d: Action.RIGHT,
    pygame.K_z: Action.INTERACT,
    pygame.K_SPACE: Action.INTERACT,
    pygame.K_RETURN: Action.INTERACT,
    pygame.K_i: Action.INVENTORY,
    pygame.K_TAB: Action.INVENTORY,
    pygame.K_ESCAPE: Action.PAUSE,
    pygame.K_p: Action.PAUSE,
}


class Input:
    def __init__(self):
        self._sources = {}       # Action -> conjunto de fontes que a seguram (teclas, toques)
        self._dir_order = []     # direcoes seguradas, da mais antiga para a mais recente
        self._pressed = set()    # Actions que comecaram a ser seguradas desde o ultimo tick

    # --- alimentacao ---------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            action = KEY_MAP.get(event.key)
            if action:
                self.press(action, ("key", event.key))
        elif event.type == pygame.KEYUP:
            action = KEY_MAP.get(event.key)
            if action:
                self.release(action, ("key", event.key))
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.release_all()  # evita tecla "presa" ao perder o foco (comum no navegador)

    def press(self, action, source):
        srcs = self._sources.setdefault(action, set())
        if not srcs:
            self._pressed.add(action)
            if action in DIRECTION_VECTORS:
                self._dir_order.append(action)
        srcs.add(source)

    def release(self, action, source):
        srcs = self._sources.get(action)
        if not srcs:
            return
        srcs.discard(source)
        if not srcs and action in self._dir_order:
            self._dir_order.remove(action)

    def release_all(self):
        self._sources.clear()
        self._dir_order.clear()

    # --- consulta (use dentro do update) ------------------------------
    def held(self, action):
        return bool(self._sources.get(action))

    def pressed(self, action):
        """True so no primeiro tick depois do aperto."""
        return action in self._pressed

    def direction(self):
        """Vetor (dx, dy) em 4 direcoes; com varias teclas, vence a mais recente."""
        for action in reversed(self._dir_order):
            if self.held(action):
                return DIRECTION_VECTORS[action]
        return (0, 0)

    def end_tick(self):
        """Chamar uma vez apos cada update da logica."""
        self._pressed.clear()
