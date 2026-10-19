"""Paisagem pintada por codigo: ceu da hora do dia, sol, nuvens, a montanha com o castelo no alto,
os trilhos da Maria Fumaca subindo a encosta, o vale com o rio e o bosque la embaixo.

Usada na tela de titulo, na abertura e na viagem de trem. Tudo em cache por hora do dia.
"""
import math

import pygame

from src import config

P = config.PALETTE
W, H = config.LOGICAL_W, config.LOGICAL_H

SKIES = {
    "tarde": ["ceu", "ceu", "agua_clara", "agua_clara", "areia_clara"],
    "entardecer": ["azul", "roxo", "rosa_escuro", "laranja", "amarelo"],
    "por_do_sol": ["contorno", "azul", "roxo", "rosa_escuro", "laranja"],
}
SUN = {"tarde": (150, 70), "entardecer": (110, 150), "por_do_sol": (90, 190)}

# trilhos: da estacao (embaixo, a esquerda) ate o castelo, em zigue-zague pela encosta
RAIL = [(150, 300), (330, 262), (250, 224), (400, 190), (330, 156), (452, 128)]
PEAK = (470, 92)


def rail_point(u):
    """Ponto (x, y) e inclinacao (graus) ao longo dos trilhos, u em 0..1."""
    segs = list(zip(RAIL, RAIL[1:]))
    lens = [math.dist(a, b) for a, b in segs]
    d = u * sum(lens)
    for (a, b), L in zip(segs, lens):
        if d <= L or (a, b) == segs[-1]:
            t = min(d / L, 1.0)
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            ang = math.degrees(math.atan2(-(b[1] - a[1]), b[0] - a[0]))
            return x, y, ang, b[0] < a[0]
        d -= L
    return RAIL[-1][0], RAIL[-1][1], 0.0, False


_cache = {}


def _static(time):
    if time in _cache:
        return _cache[time]
    s = pygame.Surface((W, H))
    sky = SKIES[time]
    s.fill(P[sky[-1]])
    band = H // 2 // len(sky) + 1
    for i, c in enumerate(sky):                                   # ceu em faixas
        s.fill(P[c], (0, i * band, W, band))
        if i + 1 < len(sky):                                      # pontilhado entre as faixas
            for x in range(0, W, 4):
                s.fill(P[sky[i + 1]], (x + (i % 2) * 2, (i + 1) * band - 2, 2, 2))
    sx, sy = SUN[time]
    pygame.draw.circle(s, P["areia_clara"], (sx, sy), 30)
    pygame.draw.circle(s, P["amarelo"], (sx, sy), 24)
    # montanhas ao fundo
    pygame.draw.polygon(s, P["rocha"], [(0, 230), (90, 150), (180, 210), (250, 160), (330, 230)])
    pygame.draw.polygon(s, P["rocha_clara"], [(560, 230), (610, 140), (640, 170), (640, 230)])
    for x, y in ((90, 150), (250, 160), (610, 140)):
        pygame.draw.polygon(s, P["branco"], [(x - 14, y + 16), (x, y), (x + 14, y + 16)])
    # a grande montanha do castelo
    mount = [(120, 330), (300, 210), (380, 150), PEAK, (560, 170), (640, 260), (640, 330)]
    pygame.draw.polygon(s, P["rocha_contorno"], mount)
    pygame.draw.polygon(s, P["rocha"], [(150, 330), (310, 215), (385, 158), PEAK, (520, 160), (600, 250), (620, 330)])
    pygame.draw.polygon(s, P["rocha_clara"], [(380, 158), PEAK, (430, 180), (360, 230)])
    for k in range(9):                                            # neve e pedras
        x = 300 + k * 32
        pygame.draw.line(s, P["rocha_contorno"], (x, 330), (x + 40, 200 + (k % 3) * 20), 2)
    pygame.draw.polygon(s, P["branco"], [(440, 112), PEAK, (500, 112), (480, 120), (465, 110), (452, 122)])
    # trilhos
    pygame.draw.lines(s, P["contorno"], False, RAIL, 5)
    for a, b in zip(RAIL, RAIL[1:]):
        n = int(math.dist(a, b) // 9)
        for i in range(n):
            t = i / max(n, 1)
            x, y = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
            pygame.draw.line(s, P["madeira"], (x - 2, y - 4), (x + 2, y + 4), 2)
    pygame.draw.lines(s, P["rocha_clara"], False, RAIL, 1)
    _castle(s, PEAK[0], PEAK[1])
    # vale verde, rio e bosque
    pygame.draw.polygon(s, P["verde_medio"], [(0, 260), (160, 290), (320, 300), (640, 300), (640, H), (0, H)])
    pygame.draw.polygon(s, P["chao"], [(0, 300), (300, 316), (640, 312), (640, H), (0, H)])
    river = [(0, 334), (120, 326), (240, 340), (380, 330), (520, 344), (640, 336)]
    pygame.draw.lines(s, P["agua"], False, river, 10)
    pygame.draw.lines(s, P["agua_clara"], False, [(x, y - 3) for x, y in river], 2)
    for k in range(26):                                           # pinheirinhos do bosque
        x = k * 25 - 6
        y = 300 + (k * 37) % 26
        if 120 < x < 330 and y < 312:
            continue
        pygame.draw.polygon(s, P["verde_escuro"], [(x, y + 26), (x + 11, y), (x + 22, y + 26)])
        pygame.draw.polygon(s, P["verde_contorno"], [(x + 11, y), (x + 22, y + 26), (x + 13, y + 26)])
        s.fill(P["madeira_escura"], (x + 9, y + 26, 4, 5))
    pygame.draw.rect(s, P["madeira"], (130, 292, 40, 10))            # estacao
    pygame.draw.polygon(s, P["vermelho"], [(126, 292), (150, 280), (174, 292)])
    _cache[time] = s
    return s


def _castle(s, cx, cy):
    """Castelo no pico: muralha, torres com telhados rosa, bandeirinhas e janelas acesas."""
    base_y = cy + 4
    pygame.draw.rect(s, P["rocha_clara"], (cx - 46, base_y - 26, 92, 30))
    for x in range(cx - 46, cx + 46, 8):
        s.fill(P["rocha_clara"], (x, base_y - 32, 5, 6))
    for tx, th in ((-40, 52), (-14, 70), (14, 62), (38, 48)):
        x = cx + tx
        pygame.draw.rect(s, P["branco"], (x - 7, base_y - th, 14, th))
        pygame.draw.rect(s, P["rocha_clara"], (x + 3, base_y - th, 4, th))
        pygame.draw.polygon(s, P["rosa"], [(x - 10, base_y - th), (x, base_y - th - 18), (x + 10, base_y - th)])
        pygame.draw.polygon(s, P["rosa_escuro"], [(x, base_y - th - 18), (x + 10, base_y - th), (x + 2, base_y - th)])
        pygame.draw.line(s, P["contorno"], (x, base_y - th - 18), (x, base_y - th - 28))
        pygame.draw.polygon(s, P["vermelho"], [(x, base_y - th - 28), (x + 9, base_y - th - 25), (x, base_y - th - 22)])
        s.fill(P["amarelo"], (x - 2, base_y - th + 12, 4, 6))
    pygame.draw.rect(s, P["madeira_escura"], (cx - 6, base_y - 14, 12, 18))
    pygame.draw.circle(s, P["madeira_escura"], (cx, base_y - 14), 6)


def draw_panorama(canvas, time="tarde", ticks=0):
    canvas.blit(_static(time), (0, 0))
    for k in range(4):                                            # nuvens passando
        x = (k * 190 + ticks * (0.2 + k * 0.05)) % (W + 160) - 80
        y = 40 + k * 22
        for dx, dy, r in ((0, 0, 14), (16, -6, 16), (34, 0, 13), (18, 4, 12)):
            pygame.draw.circle(canvas, P["branco"], (int(x + dx), y + dy), r)
