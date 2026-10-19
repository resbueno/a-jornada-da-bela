"""Arte do terreno gerada por codigo, na paleta de 32 cores, com tiles de 32x32.

Cada tile e montado de forma deterministica (mesmo mapa = mesma imagem) e guardado em cache pela
sua "assinatura" (tipo, variacao e vizinhos), entao cada desenho diferente e feito uma vez so.
O estilo do mapa (bosque, vale, montanha, castelo) muda as cores do chao.
"""
import math
import random

import pygame

from src import config
from src.world.terrain import WATERS, Terrain

T = config.TILE
P = config.PALETTE

# cores do chao por estilo: (base, sombra, brilho, tufo)
GROUND = {
    "bosque": ("chao_sombra", "verde_medio", "chao", "verde_escuro"),
    "vale": ("chao", "chao_sombra", "chao_claro", "verde_medio"),
    "montanha": ("chao_sombra", "verde_medio", "chao", "verde_escuro"),
    "castelo": ("chao", "chao_sombra", "chao_claro", "verde_medio"),
}
PATH = {
    "bosque": ("areia_sombra", "madeira", "areia"),
    "vale": ("areia", "areia_sombra", "areia_clara"),
    "montanha": ("areia", "areia_sombra", "areia_clara"),
    "castelo": ("areia", "areia_sombra", "areia_clara"),
}
LAND_PATH = {Terrain.DIRT, Terrain.GATE, Terrain.WIND}


def _h(tx, ty, salt=0):
    return ((tx * 73856093) ^ (ty * 19349663) ^ (salt * 83492791)) & 0x7FFFFFFF


class Pen:
    """Pincel sobre uma Surface, com cores pelo nome da paleta."""

    def __init__(self, w=T, h=T, base=None):
        self.s = base.copy() if base is not None else pygame.Surface((w, h), pygame.SRCALPHA)
        self.w, self.h = self.s.get_size()

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.s.set_at((x, y), P[c])

    def rect(self, x0, y0, x1, y1, c):
        x0, y0 = max(x0, 0), max(y0, 0)
        x1, y1 = min(x1, self.w - 1), min(y1, self.h - 1)
        if x1 >= x0 and y1 >= y0:
            self.s.fill(P[c], (x0, y0, x1 - x0 + 1, y1 - y0 + 1))

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                    self.px(x, y, c)

    def line(self, x0, y0, x1, y1, c):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            self.px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)

    def get(self):
        return self.s


# --------------------------------------------------------------- chao
def ground(style, i):
    base, dark, light, tuft = GROUND[style]
    rng = random.Random(1000 + i * 7 + len(style))
    p = Pen()
    p.rect(0, 0, T - 1, T - 1, base)
    for _ in range(14):                                  # pontinhos
        p.px(rng.randrange(T), rng.randrange(T), dark if rng.random() < 0.6 else light)
    for _ in range(4 if style != "montanha" else 2):     # tufos de capim
        x, y = rng.randrange(3, T - 4), rng.randrange(5, T - 2)
        p.line(x, y, x - 1, y - 3, tuft); p.line(x + 2, y, x + 2, y - 4, tuft); p.line(x + 4, y, x + 5, y - 3, tuft)
        p.px(x + 2, y - 4, light)
    if style == "montanha":                              # pedrinhas e um tufo verde
        for _ in range(3):
            x, y = rng.randrange(2, T - 4), rng.randrange(2, T - 3)
            p.rect(x, y, x + 2, y + 1, "rocha"); p.px(x, y, "branco")
    if style == "bosque" and i == 3:                     # cogumelinho
        p.rect(20, 22, 21, 25, "areia_clara"); p.ellipse(21, 21, 3.5, 2.2, "vermelho"); p.px(20, 20, "branco")
    return p.get()


def flowers(style, i):
    p = Pen(base=ground(style, i))
    rng = random.Random(3000 + i)
    for _ in range(5):
        x, y = rng.randrange(3, T - 4), rng.randrange(3, T - 4)
        petal, mid = rng.choice((("vermelho", "amarelo"), ("rosa", "amarelo"), ("branco", "amarelo"), ("roxo", "branco")))
        p.px(x, y + 3, "verde_escuro"); p.px(x, y + 4, "verde_escuro")
        for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1)):
            p.px(x + dx, y + dy, petal)
        p.px(x, y, mid)
    return p.get()


def tall_grass(style, i):
    p = Pen(base=ground(style, i % 4))
    dark = "verde_contorno" if style == "bosque" else "verde_escuro"
    for ox, oy in ((2, 4), (16, 2), (9, 16), (22, 18)) if i % 2 == 0 else ((4, 2), (18, 6), (6, 18), (20, 20)):
        bx, by = ox + 5, oy + 12
        for ex, ey in ((0, 5), (2, 1), (5, 0), (8, 2), (10, 6)):
            tx, ty = ox + ex, oy + ey
            p.line(bx, by, tx, ty, dark)
            p.px((bx + tx) // 2, (by + ty) // 2, "verde_medio")
            p.px(tx, ty, "verde_claro")
        p.rect(bx - 1, by, bx + 1, by, "verde_contorno")
    return p.get()


# --------------------------------------------------------------- trilha
def path_base(style, i):
    base, dark, light = PATH[style]
    rng = random.Random(2000 + i)
    p = Pen()
    p.rect(0, 0, T - 1, T - 1, base)
    for _ in range(18):
        p.px(rng.randrange(T), rng.randrange(T), dark)
    for _ in range(10):
        p.px(rng.randrange(T), rng.randrange(T), light)
    for _ in range(2):                                   # pedrinhas
        x, y = rng.randrange(2, T - 4), rng.randrange(2, T - 3)
        p.rect(x, y, x + 1, y + 1, "rocha_clara"); p.px(x + 1, y + 1, "rocha")
    return p.get()


# --------------------------------------------------------------- arvores e pedras
def big_pine(style, i):
    """Pinheiro 64x64 em 3 camadas, com tronco e sombra; vira 4 quadrantes de 32x32."""
    rng = random.Random(5000 + i)
    S = 2 * T
    p = Pen(S, S)
    light, mid, dark, edge = ("verde_claro", "verde_medio", "verde_escuro", "verde_contorno")
    if style == "bosque":
        light, mid, dark = "verde_medio", "verde_escuro", "verde_contorno"
    if style == "montanha":
        light = "verde_brilho"
    for x in range(14, 50):                              # sombra no chao
        for y in range(58, 64):
            if (x - 31.5) ** 2 / 300 + (y - 62) ** 2 / 9 <= 1:
                p.px(x, y, GROUND[style][1])
    p.rect(28, 54, 35, 63, "madeira")                    # tronco
    p.rect(28, 54, 29, 63, "madeira_escura"); p.rect(34, 54, 35, 63, "madeira_escura")
    tiers = [(2, 22, 10, 34), (18, 22, 22, 50), (34, 22, 38, 62)]
    for start, rows, w0, w1 in tiers:
        for r in range(rows):
            w = w0 + (w1 - w0) * r // (rows - 1)
            w -= w % 2
            x0 = (S - w) // 2
            last = r >= rows - 2
            for x in range(w):
                y = start + r
                if x <= 1 or x >= w - 2:
                    c = edge
                elif last:
                    c = edge if (x // 2) % 2 == 0 else dark
                else:
                    u = (x - (w - 1) / 2) / max((w - 1) / 2, 1)
                    c = light if u < -0.45 else (mid if u < 0.15 else dark)
                    if u < -0.65 and r < rows - 5 and rng.random() < 0.5:
                        c = "verde_brilho" if style != "bosque" else "verde_claro"
                    elif r % 6 == 3 and rng.random() < 0.3:
                        c = dark if c != dark else mid
                p.px(x0 + x, y, c)
    if style == "montanha":                              # neve nas pontas dos galhos
        for start, rows, w0, w1 in tiers:
            for x in range(-w0 // 2 + 2, w0 // 2 - 2, 3):
                p.px(S // 2 + x, start + 1, "branco")
    s = p.get()
    return [[s.subsurface((qx * T, qy * T, T, T)).copy() for qx in range(2)] for qy in range(2)]


def rock(base):
    p = Pen(base=base)
    for x in range(6, 28):                               # sombra
        p.px(x, 28, "chao_sombra" if base is None else "rocha_contorno")
    for y in range(5, 29):
        for x in range(3, 29):
            dx, dy = (x - 15.5) / 12.5, (y - 17) / 10.5
            d = dx * dx + dy * dy
            if d <= 1.0:
                if d > 0.82:
                    c = "rocha_contorno"
                elif dx + dy < -0.45:
                    c = "rocha_clara"
                elif dx + dy > 0.5:
                    c = "rocha_contorno" if (x + y) % 3 == 0 else "rocha"
                else:
                    c = "rocha"
                p.px(x, y, c)
    p.rect(9, 9, 11, 10, "branco"); p.rect(12, 10, 14, 10, "rocha_clara")
    p.line(17, 15, 21, 20, "rocha_contorno")             # rachadura
    p.rect(6, 20, 9, 22, "verde_medio"); p.px(7, 19, "verde_claro")   # musgo
    return p.get()


# --------------------------------------------------------------- agua
def water(frame, i, n, s, w, e, rapids=False):
    rng = random.Random(7000 + i)
    p = Pen()
    p.rect(0, 0, T - 1, T - 1, "agua")
    if rapids:                                           # correnteza: riscos brancos descendo
        for k in range(5):
            x = rng.randrange(2, T - 3)
            y0 = (rng.randrange(T) + frame * 10) % T
            for d in range(7):
                p.px(x + (d // 4), (y0 + d) % T, "agua_clara" if d < 5 else "branco")
        for _ in range(6):
            p.px(rng.randrange(T), rng.randrange(T), "agua_escura")
    else:
        for _ in range(4):
            x, y = rng.randrange(T - 8), rng.randrange(2, T - 2)
            shift = (frame * 3) % 6
            p.rect(x + shift, y, x + shift + 4, y, "agua_clara")
            p.px(x + shift - 1, y + 1, "agua_escura"); p.px(x + shift + 5, y + 1, "agua_escura")
    for ok, side in ((n, "n"), (s, "s"), (w, "w"), (e, "e")):
        if ok:
            continue
        for k in range(T):
            foam = "branco" if (k + frame * 2) % 5 == 0 else "agua_clara"
            if side == "n":
                p.px(k, 0, "areia_sombra"); p.px(k, 1, foam); p.px(k, 2, "agua_clara" if k % 3 else "agua")
            elif side == "s":
                p.px(k, T - 1, "areia_sombra"); p.px(k, T - 2, foam)
            elif side == "w":
                p.px(0, k, "areia_sombra"); p.px(1, k, foam)
            else:
                p.px(T - 1, k, "areia_sombra"); p.px(T - 2, k, foam)
    return p.get()


def post(base):
    """Pilar da ponte antiga, quebrada: so sobrou a madeira saindo da agua."""
    p = Pen(base=base)
    p.ellipse(16, 26, 11, 4, "agua_clara")
    p.rect(9, 8, 22, 26, "madeira")
    p.rect(9, 8, 11, 26, "madeira_escura"); p.rect(20, 8, 22, 26, "madeira_escura")
    p.rect(9, 6, 22, 8, "areia")                         # topo serrado
    p.line(9, 7, 14, 5, "areia_clara"); p.line(16, 5, 22, 8, "areia_sombra")
    p.rect(9, 14, 22, 15, "rocha_contorno")              # cinta de ferro
    p.px(12, 14, "rocha_clara"); p.px(19, 14, "rocha_clara")
    for x in range(8, 24, 3):
        p.px(x, 27, "branco")
    return p.get()


# --------------------------------------------------------------- obstaculos
def fissure(i, n_open, s_open):
    """Desfiladeiro: borda de rocha em cima, paredes em camadas e o fundo escuro."""
    rng = random.Random(9000 + i)
    p = Pen()
    p.rect(0, 0, T - 1, T - 1, "contorno")
    for y in range(T):
        band = "rocha_contorno" if (y // 4) % 2 else "rocha"
        if y > 14:
            band = "contorno" if (y + i) % 5 else "rocha_contorno"
        for x in range(T):
            if (x * 3 + y * 7 + i) % 11 < 4:
                p.px(x, y, band)
    for _ in range(4):
        p.px(rng.randrange(T), rng.randrange(18, T), "roxo")   # brilhinhos la no fundo
    if n_open:                                           # beirada de cima, iluminada
        p.rect(0, 0, T - 1, 3, "rocha_clara"); p.rect(0, 4, T - 1, 6, "rocha")
        for x in range(0, T, 4):
            p.px(x + 1, 7, "rocha"); p.px(x + 2, 3, "branco")
    if s_open:                                           # beirada de baixo
        p.rect(0, T - 3, T - 1, T - 1, "rocha"); p.rect(0, T - 1, T - 1, T - 1, "rocha_clara")
    return p.get()


def thorns(base, i, frame):
    """Espinheiro magico: galhos roxo-escuros enrolados com espinhos rosa que brilham."""
    rng = random.Random(9500 + i)
    p = Pen(base=base)
    p.ellipse(16, 26, 15, 5, "verde_contorno")
    for k in range(6):
        x0 = 3 + k * 5 + rng.randint(-1, 1)
        h = rng.randint(16, 27)
        for j in range(h):
            x = x0 + round(math.sin((j + k) / 3.0) * 2)
            y = T - 2 - j
            p.px(x, y, "roxo" if j % 4 else "contorno"); p.px(x + 1, y, "contorno")
            if j % 6 == 3:
                p.px(x - 1, y - 1, "rosa"); p.px(x + 2, y - 1, "rosa")
        p.px(x0, T - 3 - h, "rosa_escuro")
    for _ in range(4):                                   # brilho magico (pisca entre quadros)
        x, y = rng.randrange(2, T - 2), rng.randrange(4, T - 6)
        if (x + frame) % 2:
            p.px(x, y, "branco"); p.px(x + 1, y, "rosa")
    return p.get()


def cliff(i, below_open, style):
    """Paredao de rocha: topo com rachaduras; com chao embaixo, mostra a face em camadas."""
    rng = random.Random(9800 + i)
    p = Pen()
    p.rect(0, 0, T - 1, T - 1, "rocha")
    for _ in range(26):
        p.px(rng.randrange(T), rng.randrange(T), rng.choice(("rocha_contorno", "rocha_clara", "rocha")))
    if style == "montanha" and i % 3 == 0:               # neve no topo
        p.ellipse(10 + i % 7, 8, 7, 3, "branco"); p.ellipse(9 + i % 7, 7, 4, 1.5, "agua_clara")
    if below_open:
        for y in range(14, T):
            for x in range(T):
                c = "rocha_contorno" if (x * 5 + y * 3 + i) % 9 < 3 else ("rocha" if y < 22 else "rocha_contorno")
                if y > 27:
                    c = "contorno" if (x + y) % 3 else "rocha_contorno"
                p.px(x, y, c)
        p.rect(0, 12, T - 1, 13, "rocha_clara")
        for x in range(0, T, 5):
            p.line(x + 2, 15, x + 1, 26, "rocha_contorno")
    return p.get()


def wind(base, frame, i):
    """Trilha de vento: riscos brancos atravessando (mudam a cada quadro)."""
    p = Pen(base=base)
    rng = random.Random(9900 + i)
    for _ in range(3):
        y = rng.randrange(3, T - 3)
        x = (rng.randrange(T) + frame * 12) % T
        for d in range(9):
            p.px((x + d) % T, y + (1 if d > 6 else 0), "branco" if d % 3 else "agua_clara")
    return p.get()


def rail(base, horizontal):
    p = Pen(base=base)
    if horizontal:
        p.rect(0, 9, T - 1, 23, "areia_sombra")          # cascalho
        for x in range(1, T, 4):
            p.px(x, 10 + x % 11, "rocha"); p.px(x + 2, 21 - x % 9, "rocha_clara")
        for x in (3, 13, 23):                            # dormentes
            p.rect(x, 7, x + 5, 25, "madeira_escura"); p.rect(x, 7, x + 5, 8, "madeira")
        for y in (11, 20):                               # trilhos de aco
            p.rect(0, y, T - 1, y + 1, "rocha_clara"); p.rect(0, y, T - 1, y, "branco")
            p.rect(0, y + 2, T - 1, y + 2, "rocha_contorno")
    else:
        p.rect(9, 0, 23, T - 1, "areia_sombra")
        for y in (3, 13, 23):
            p.rect(7, y, 25, y + 5, "madeira_escura"); p.rect(7, y, 25, y, "madeira")
        for x in (11, 20):
            p.rect(x, 0, x + 1, T - 1, "rocha_clara"); p.rect(x, 0, x, T - 1, "branco")
            p.rect(x + 2, 0, x + 2, T - 1, "rocha_contorno")
    return p.get()


def planks(horizontal, i):
    p = Pen()
    p.rect(0, 0, T - 1, T - 1, "madeira")
    for k in range(4):
        a = k * 8
        if horizontal:
            p.rect(0, a + 7, T - 1, a + 7, "madeira_escura"); p.rect(0, a, T - 1, a, "areia_sombra")
            off = (k * 11 + i * 5) % T
            p.rect(off, a, off, a + 6, "madeira_escura")
            p.px((off + 4) % T, a + 3, "rocha_contorno"); p.px((off + 27) % T, a + 3, "rocha_contorno")
        else:
            p.rect(a + 7, 0, a + 7, T - 1, "madeira_escura"); p.rect(a, 0, a, T - 1, "areia_sombra")
            off = (k * 11 + i * 5) % T
            p.rect(a, off, a + 6, off, "madeira_escura")
            p.px(a + 3, (off + 4) % T, "rocha_contorno")
    return p.get()


def lamp(base, frame):
    """Poste de ferro com lampiao aceso."""
    p = Pen(base=base)
    p.ellipse(16, 29, 7, 2, "rocha_contorno")
    p.rect(15, 10, 17, 29, "contorno"); p.rect(15, 10, 15, 29, "azul")
    p.rect(12, 27, 20, 29, "contorno")
    p.rect(10, 0, 22, 2, "contorno")                     # teto do lampiao
    p.rect(11, 3, 21, 10, "contorno")
    glow = "amarelo" if frame == 0 else "areia_clara"
    p.rect(12, 4, 20, 9, glow); p.rect(15, 5, 17, 8, "branco")
    return p.get()


def stone_floor(i):
    rng = random.Random(4000 + i)
    p = Pen()
    p.rect(0, 0, T - 1, T - 1, "rocha_clara")
    for y0, x0s in ((0, (0, 18)), (16, (8, 26))):        # lajotas desencontradas
        p.rect(0, y0, T - 1, y0, "rocha")
        for x in x0s:
            p.rect(x, y0, x, y0 + 15, "rocha")
    for _ in range(10):
        p.px(rng.randrange(T), rng.randrange(T), rng.choice(("rocha", "areia_clara")))
    return p.get()


def castle_wall(top, bottom):
    """Muralha branca-creme, como o castelo visto de longe."""
    p = Pen()
    p.rect(0, 0, T - 1, T - 1, "areia_clara")
    for y in range(0, T, 8):                             # tijolos
        p.rect(0, y + 7, T - 1, y + 7, "areia_sombra")
        off = 8 if (y // 8) % 2 else 0
        for x in range(off, T, 16):
            p.rect(x, y, x, y + 6, "areia_sombra")
        for x in range(off + 2, T, 16):
            p.rect(x, y + 1, x + 4, y + 1, "branco")
    if top:                                              # ameias
        for x in range(T):
            for y in range(0, 8):
                if (x // 8) % 2 == 0:
                    p.px(x, y, "ceu" if y < 6 else "rocha_contorno")
        p.rect(0, 8, T - 1, 9, "rocha_contorno")
    if bottom:
        p.rect(0, T - 2, T - 1, T - 1, "rocha_contorno")
    return p.get()


def castle_gate(col, cols, row, rows, opened=False):
    """Portao de madeira com cintas de ferro, arco no alto. (col,row) dentro do bloco do portao.
    Aberto: o arco mostra o salao iluminado la dentro."""
    p = Pen(base=castle_wall(False, False))
    W, H = cols * T, rows * T
    for y in range(T):
        for x in range(T):
            gx, gy = col * T + x, row * T + y
            cx = W / 2
            r = W / 2 - 2
            inside = gx >= 2 and gx < W - 2 and (gy >= r or (gx - cx) ** 2 + (gy - r) ** 2 <= r * r)
            if not inside:
                continue
            edge = gx < 5 or gx >= W - 5 or ((gx - cx) ** 2 + (gy - r) ** 2 >= (r - 3) ** 2 and gy < r)
            if edge:
                c = "rocha_contorno"
            elif opened:
                c = "amarelo" if gy > H - 20 else ("laranja" if (gx + gy) % 7 else "areia_clara")
            else:
                c = "madeira" if (gx // 8) % 2 else "madeira_escura"
                if gy % 24 in (10, 11):
                    c = "contorno"                           # cintas de ferro
                if abs(gx - cx) < 1:
                    c = "contorno"
            p.px(x, y, c)
    if row == rows - 1 and not opened:                   # argolas
        for gx in (W / 2 - 10, W / 2 + 8):
            lx = int(gx) - col * T
            if 0 <= lx < T:
                p.ellipse(lx + 1, 10, 3, 3, "amarelo"); p.ellipse(lx + 1, 10, 1.5, 1.5, "madeira_escura")
    return p.get()


def gate(base, frame):
    """Passagem para o proximo mapa: trilha com brilhos girando."""
    p = Pen(base=base)
    for k in range(6):
        a = k * math.tau / 6 + frame * 0.5
        x, y = 16 + math.cos(a) * 10, 16 + math.sin(a) * 6
        p.rect(int(x), int(y), int(x) + 1, int(y) + 1, "branco" if k % 2 else "amarelo")
    p.ellipse(16, 16, 3, 2, "rosa")
    return p.get()


# ================================================================= mapa
class MapArt:
    def __init__(self, world, style="vale"):
        self.world = world
        self.style = style if style in GROUND else "vale"
        self.cache = {}
        self.pines = [big_pine(self.style, i) for i in range(2)]
        gates = [(x, y) for y in range(world.rows) for x in range(world.cols)
                 if world.grid[y][x] is Terrain.CASTLE_GATE]
        self.gate_box = None
        if gates:
            xs, ys = [g[0] for g in gates], [g[1] for g in gates]
            self.gate_box = (min(xs), min(ys), max(xs) - min(xs) + 1, max(ys) - min(ys) + 1)

    def _get(self, key, make):
        s = self.cache.get(key)
        if s is None:
            s = make()
            self.cache[key] = s
        return s

    def _kind(self, tx, ty):
        w = self.world
        if 0 <= tx < w.cols and 0 <= ty < w.rows:
            return w.grid[ty][tx]
        return None

    def _same(self, tx, ty, group):
        k = self._kind(tx, ty)
        return k is None or k in group

    def _ground(self, tx, ty):
        v = _h(tx, ty) % 4
        if _h(tx, ty, 3) % 13 == 0 and self.style != "montanha":
            return self._get(("flowers_rare", v), lambda: flowers(self.style, v + 10))
        return self._get(("ground", v), lambda: ground(self.style, v))

    def _path(self, tx, ty):
        v = _h(tx, ty) % 3
        g = _h(tx, ty, 1) % 4
        grp = LAND_PATH | {Terrain.RAIL, Terrain.PLANKS}
        sides = tuple(self._same(tx + dx, ty + dy, grp) for dx, dy in ((0, -1), (1, 0), (0, 1), (-1, 0)))
        diag = tuple(self._same(tx + dx, ty + dy, grp) for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)))
        return self._get(("path", v, g, sides, diag), lambda: self._make_path(v, g, sides, diag))

    def _make_path(self, v, gv, sides, diag):
        n, e, so, w = sides
        s = path_base(self.style, v).copy()
        g = self._get(("ground", gv), lambda: ground(self.style, gv))
        dark = PATH[self.style][1]
        for y in range(T):
            for x in range(T):
                best = None
                for ok, d in ((n, y), (so, T - 1 - y), (w, x), (e, T - 1 - x)):
                    if not ok and d <= 3:
                        best = d if best is None else min(best, d)
                if best is None:
                    continue
                wob = (x * 5 + y * 3) % 5
                if best <= 1 or (best == 2 and wob != 4):
                    s.set_at((x, y), g.get_at((x, y)))
                elif best <= 3:
                    s.set_at((x, y), P[dark])
        for k, (dx, dy) in enumerate(((0, 0), (1, 0), (0, 1), (1, 1))):   # cantos concavos
            if n and so and w and e and not diag[k]:
                cx, cy = dx * (T - 1), dy * (T - 1)
                for ox in range(3):
                    for oy in range(3 - ox):
                        px = cx + (ox if dx == 0 else -ox)
                        py = cy + (oy if dy == 0 else -oy)
                        s.set_at((px, py), g.get_at((px, py)))
        return s

    def _water(self, tx, ty, frame, rapids):
        v = _h(tx, ty) % 3
        sides = tuple(self._same(tx + dx, ty + dy, WATERS | {Terrain.ROCK, Terrain.POST})
                      for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)))
        return self._get(("water", frame, v, sides, rapids), lambda: water(frame, v, *sides, rapids=rapids))

    def _tile(self, tx, ty, frame):
        kind = self.world.grid[ty][tx]
        st = self.style
        if kind is Terrain.DIRT:
            return self._path(tx, ty)
        if kind in WATERS:
            return self._water(tx, ty, frame, kind is Terrain.RAPIDS)
        if kind is Terrain.GATE:
            base = self._path(tx, ty)
            return self._get(("gate", frame, id(base)), lambda: gate(base, frame))
        if kind is Terrain.WIND:
            base = self._path(tx, ty)
            return self._get(("wind", frame, id(base)), lambda: wind(base, frame, _h(tx, ty) % 3))
        if kind is Terrain.TALL_GRASS:
            v = (tx + ty) % 2
            return self._get(("tall", v), lambda: tall_grass(st, v))
        if kind is Terrain.FLOWERS:
            v = _h(tx, ty) % 4
            return self._get(("flowers", v), lambda: flowers(st, v))
        if kind is Terrain.TREE:
            base = self._ground(tx, ty)
            q = self.pines[((tx // 2) + (ty // 2)) % 2][ty % 2][tx % 2]
            return self._get(("tree", id(base), id(q)), lambda: _over(base, q))
        if kind is Terrain.ROCK:
            near = [self._kind(tx + dx, ty + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
            if any(k in WATERS for k in near):
                base = self._water(tx, ty, frame, any(k is Terrain.RAPIDS for k in near))
            elif any(k is Terrain.DIRT for k in near):
                base = self._path(tx, ty)
            else:
                base = self._ground(tx, ty)
            return self._get(("rock", id(base)), lambda: rock(base))
        if kind is Terrain.POST:
            base = self._water(tx, ty, frame, False)
            return self._get(("post", id(base)), lambda: post(base))
        if kind is Terrain.FISSURE:
            n = self._kind(tx, ty - 1) is not Terrain.FISSURE
            s = self._kind(tx, ty + 1) is not Terrain.FISSURE
            v = _h(tx, ty) % 3
            return self._get(("fissure", v, n, s), lambda: fissure(v, n, s))
        if kind is Terrain.THORN:
            base = self._ground(tx, ty)
            v = _h(tx, ty) % 3
            return self._get(("thorn", v, frame, id(base)), lambda: thorns(base, v, frame))
        if kind is Terrain.CLIFF:
            below = self._kind(tx, ty + 1)
            open_ = below is not None and below is not Terrain.CLIFF
            v = _h(tx, ty) % 6
            return self._get(("cliff", v, open_), lambda: cliff(v, open_, st))
        if kind is Terrain.RAIL:
            hz = self._kind(tx - 1, ty) is Terrain.RAIL or self._kind(tx + 1, ty) is Terrain.RAIL
            base = self._ground(tx, ty)
            return self._get(("rail", hz, id(base)), lambda: rail(base, hz))
        if kind is Terrain.PLANKS:
            hz = not (self._kind(tx, ty - 1) is Terrain.PLANKS and self._kind(tx, ty + 1) is Terrain.PLANKS
                      and self._kind(tx - 1, ty) is not Terrain.PLANKS)
            v = _h(tx, ty) % 3
            return self._get(("planks", hz, v), lambda: planks(hz, v))
        if kind is Terrain.LAMP:
            base = self._ground(tx, ty)
            return self._get(("lamp", frame, id(base)), lambda: lamp(base, frame))
        if kind is Terrain.STONE:
            v = _h(tx, ty) % 3
            return self._get(("stone", v), lambda: stone_floor(v))
        if kind is Terrain.CASTLE_WALL:
            grp = {Terrain.CASTLE_WALL, Terrain.CASTLE_GATE}
            top = self._kind(tx, ty - 1) not in grp
            bottom = self._kind(tx, ty + 1) not in grp
            return self._get(("wall", top, bottom), lambda: castle_wall(top, bottom))
        if kind is Terrain.CASTLE_GATE and self.gate_box:
            gx, gy, gw, gh = self.gate_box
            col, row = tx - gx, ty - gy
            opened = getattr(self.world, "gate_open", False)
            return self._get(("cgate", col, row, opened), lambda: castle_gate(col, gw, row, gh, opened))
        return self._ground(tx, ty)

    def render(self, frame):
        """Mapa inteiro (usado em testes e previas)."""
        return self.render_region(0, 0, self.world.cols, self.world.rows, frame)

    def render_region(self, x0, y0, cols, rows, frame):
        """Desenha so um retangulo de tiles [x0, x0+cols) x [y0, y0+rows) (um 'pedaco' do mapa)."""
        w = self.world
        surf = pygame.Surface((cols * T, rows * T))
        for ty in range(y0, min(y0 + rows, w.rows)):
            for tx in range(x0, min(x0 + cols, w.cols)):
                surf.blit(self._tile(tx, ty, frame), ((tx - x0) * T, (ty - y0) * T))
        return surf


def _over(base, top):
    s = base.copy()
    s.blit(top, (0, 0))
    return s
