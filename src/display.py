"""Canvas logico 320x180 com upscale por fator inteiro (nearest) e letterbox."""
import sys

import pygame

from src import config

WEB = sys.platform == "emscripten"   # rodando no navegador (pygbag)


def _initial_size():
    """Janela inicial: 16:9 grande (escala inteira 4x); em pe (celular) so se a tela for claramente vertical."""
    landscape = (config.LOGICAL_W * config.START_SCALE, config.LOGICAL_H * config.START_SCALE)
    w = h = 0
    try:  # navegador (pygbag): tamanho da pagina
        import platform

        w, h = platform.window.innerWidth, platform.window.innerHeight
    except Exception:
        try:
            w, h = pygame.display.get_desktop_sizes()[0]
        except Exception:
            pass
    if w and h and h > w * 1.15:         # claramente vertical (celular em pe)
        pw = config.LOGICAL_W
        return (pw, round(pw * h / w))
    return landscape


class Display:
    def __init__(self):
        # no navegador o tamanho e fixo: o pygbag usa a proporcao dele para encher a pagina
        flags = 0 if WEB else pygame.RESIZABLE
        self.window = pygame.display.set_mode(_initial_size(), flags)
        self.touch = None  # TouchControls, definido pelo main
        pygame.display.set_caption(config.TITLE)
        self.canvas = pygame.Surface((config.LOGICAL_W, config.LOGICAL_H))
        self.scale = config.START_SCALE
        self.offset = (0, 0)
        self._layout()

    def _layout(self):
        """Recalcula escala inteira e deslocamento (letterbox) para o tamanho atual da janela."""
        w, h = self.window.get_size()
        self.scale = max(1, min(w // config.LOGICAL_W, h // config.LOGICAL_H))
        out_w = config.LOGICAL_W * self.scale
        out_h = config.LOGICAL_H * self.scale
        self.portrait = h > w
        # em pe: canvas no topo (controles abaixo); deitado: centralizado
        self.offset = ((w - out_w) // 2, 0 if self.portrait else (h - out_h) // 2)

    def canvas_rect(self):
        return pygame.Rect(self.offset, (config.LOGICAL_W * self.scale, config.LOGICAL_H * self.scale))

    def present(self):
        """Escala o canvas para a janela e mostra o frame."""
        self.window = pygame.display.get_surface()
        self._layout()
        self.window.fill(config.PALETTE["contorno"])
        scaled = pygame.transform.scale(
            self.canvas,
            (config.LOGICAL_W * self.scale, config.LOGICAL_H * self.scale),
        )
        self.window.blit(scaled, self.offset)
        if self.touch:
            self.touch.draw(self.window, self)
        pygame.display.flip()

    def to_logical(self, x, y):
        """Converte coordenadas da janela (ex.: toque) para coordenadas do canvas logico."""
        lx = (x - self.offset[0]) // self.scale
        ly = (y - self.offset[1]) // self.scale
        return lx, ly
