"""Controles de toque: direcional + botoes (interagir, inventario, pausa).

Celular em pe: ficam fora da imagem, na area abaixo do canvas.
Celular deitado: ficam semitransparentes sobre o jogo, nos cantos.
Alimenta o mesmo Input do teclado, com uma fonte propria por dedo.
"""
import math

import pygame

from src import config
from src.input import Action
from src.text import draw_text

DPAD_DEAD = 0.28  # fracao do raio sem direcao (centro do direcional)


class TouchControls:
    def __init__(self):
        self.seen_touch = False
        self.fingers = {}  # id do dedo -> Action atualmente segurada

    # --- layout --------------------------------------------------------
    def visible(self, display):
        return config.TOUCH_ALWAYS or self.seen_touch or display.portrait

    def layout(self, display):
        """Geometria em pixels da janela: {'dpad': (cx, cy, r), 'buttons': [(Action, rotulo, cx, cy, r)]}"""
        w, h = display.window.get_size()
        if display.portrait:
            top = display.canvas_rect().bottom
            zone_h = h - top
            u = min(w / 10.5, zone_h / 5.5)
            cy = top + zone_h * 0.5
            dpad_r = u * 1.9
            dpad = (max(w * 0.26, dpad_r * 1.2 + 10), cy, dpad_r)
            buttons = [
                (Action.INTERACT, "A", w * 0.76, cy + u * 0.5, u * 1.0),
                (Action.INVENTORY, "I", w * 0.60, cy - u * 1.0, u * 0.65),
                (Action.PAUSE, "||", w * 0.90, cy - u * 1.0, u * 0.65),
            ]
        else:
            u = h / 9.5
            dpad = (u * 2.6, h - u * 2.6, u * 1.9)
            buttons = [
                (Action.INTERACT, "A", w - u * 2.2, h - u * 2.2, u * 1.0),
                (Action.INVENTORY, "I", w - u * 4.4, h - u * 1.4, u * 0.65),
                (Action.PAUSE, "||", w - u * 1.4, h - u * 4.4, u * 0.65),
            ]
        return {"dpad": dpad, "buttons": buttons}

    def action_at(self, display, x, y):
        lay = self.layout(display)
        cx, cy, r = lay["dpad"]
        dx, dy = x - cx, y - cy
        dist = math.hypot(dx, dy)
        if r * DPAD_DEAD < dist <= r * 1.35:
            if abs(dx) > abs(dy):
                return Action.RIGHT if dx > 0 else Action.LEFT
            return Action.DOWN if dy > 0 else Action.UP
        for action, _label, bx, by, br in lay["buttons"]:
            if math.hypot(x - bx, y - by) <= br * 1.25:
                return action
        return None

    # --- eventos -------------------------------------------------------
    def handle_event(self, event, display, inp):
        t = event.type
        if t in (pygame.FINGERDOWN, pygame.FINGERMOTION, pygame.FINGERUP):
            self.seen_touch = True
            w, h = display.window.get_size()
            self._track(("finger", event.finger_id), event.x * w, event.y * h,
                        t != pygame.FINGERUP, display, inp)
        elif t in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            if getattr(event, "touch", False) or not self.visible(display):
                return  # toques ja chegam como FINGER*; mouse so conta com os botoes visiveis
            if t == pygame.MOUSEMOTION and not event.buttons[0]:
                return
            if t != pygame.MOUSEMOTION and event.button != 1:
                return
            self._track(("mouse",), event.pos[0], event.pos[1], t != pygame.MOUSEBUTTONUP, display, inp)
        elif t == pygame.WINDOWFOCUSLOST:
            self.fingers.clear()

    def _track(self, finger, x, y, down, display, inp):
        old = self.fingers.get(finger)
        new = self.action_at(display, x, y) if down else None
        if new is old:
            return
        if old is not None:
            inp.release(old, ("touch", finger))
        if new is not None:
            inp.press(new, ("touch", finger))
            self.fingers[finger] = new
        else:
            self.fingers.pop(finger, None)

    # --- desenho -------------------------------------------------------
    def draw(self, window, display):
        if not self.visible(display):
            return
        lay = self.layout(display)
        held = set(self.fingers.values())
        p = config.PALETTE
        alpha = 255 if display.portrait else 120
        w, h = window.get_size()
        layer = pygame.Surface((w, h), pygame.SRCALPHA)

        def disc(cx, cy, r, color, on):
            fill = p["amarelo_brilho"] if on else color
            pygame.draw.circle(layer, (*fill, alpha), (round(cx), round(cy)), round(r))
            pygame.draw.circle(layer, (*p["creme"], alpha), (round(cx), round(cy)), round(r), 2)

        cx, cy, r = lay["dpad"]
        disc(cx, cy, r * 1.2, p["sombra_caverna"], False)
        arm = r * 0.62
        for action, (ox, oy) in {
            Action.UP: (0, -1), Action.DOWN: (0, 1), Action.LEFT: (-1, 0), Action.RIGHT: (1, 0),
        }.items():
            disc(cx + ox * arm, cy + oy * arm, r * 0.38, p["pedra_escura"], action in held)
        for action, label, bx, by, br in lay["buttons"]:
            disc(bx, by, br, p["rosa"] if action is Action.INTERACT else p["lilas_magia"], action in held)
        window.blit(layer, (0, 0))
        for action, label, bx, by, br in lay["buttons"]:
            size = round(br * 1.3)
            draw_text(window, label, round(bx), round(by - size * 0.3), p["contorno"], size=size, center=True)
