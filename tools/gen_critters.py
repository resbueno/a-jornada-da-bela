#!/usr/bin/env python3
"""Gera os bichos do mundo como sprites em art/src/ (grades de caracteres, paleta de 32 cores).

coelho (3 cores, 4 poses: sentado, orelha mexendo, agachado, no ar), passaro (3 cores, 4 poses),
peixe (2 cores, 4 poses), enguia sombria (32x16, 4 quadros) e lacaio da Sombra (16x24).
Uso: python3 tools/gen_critters.py   (depois: build_sprites.py art/src assets/sprites)
"""
import math
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "art" / "src"


class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = [["."] * w for _ in range(h)]

    def px(self, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c, shade=None, light=None):
        """Elipse com luz de cima-esquerda: tom claro no topo-esquerda e escuro embaixo."""
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    col = c
                    if light and (y - cy) < -ry * 0.35 and (x - cx) < rx * 0.25:
                        col = light
                    elif shade and (y - cy) > ry * 0.35:
                        col = shade
                    self.px(x, y, col)

    def line(self, x0, y0, x1, y1, c):
        steps = int(max(abs(x1 - x0), abs(y1 - y0))) or 1
        for i in range(steps + 1):
            self.px(x0 + (x1 - x0) * i / steps, y0 + (y1 - y0) * i / steps, c)

    def outline(self, color="r"):
        src = [row[:] for row in self.g]
        for y in range(self.h):
            for x in range(self.w):
                if src[y][x] != ".":
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and src[ny][nx] != ".":
                        self.g[y][x] = color
                        break

    def lines(self):
        return ["".join(r) for r in self.g]


def save(name, frames, note):
    body = "\n---\n".join("\n".join(f) for f in frames)
    (OUT / f"{name}.sprite.txt").write_text(f"# {note}\n{body}\n", encoding="utf-8")


# ================================================================= COELHO
RABBITS = {
    "white": dict(W="n", S="a", D="d", B="n", P="t", L="n"),
    "brown": dict(W="f", S="e", D="b", B="a", P="t", L="a"),
    "gray": dict(W="d", S="c", D="b", B="n", P="t", L="a"),
}


def rabbit(c, pose):
    g = Grid(16, 16)
    W, S, D, B, P = c["W"], c["S"], c["D"], c["B"], c["P"]
    if pose in ("sit", "sit2"):
        # orelhas (a de tras mexe no quadro sit2)
        sway = 1 if pose == "sit2" else 0
        for k, y in enumerate(range(1, 8)):                    # orelha de tras
            g.px(8 + (1 if y < 4 else 0) + sway * (1 if y < 3 else 0), y, S)
            g.px(9 + (1 if y < 4 else 0) + sway * (1 if y < 3 else 0), y, S)
        for y in range(1, 8):                                   # orelha da frente
            g.px(5 + (1 if y < 4 else 0), y, W)
            g.px(6 + (1 if y < 4 else 0), y, W)
            if 2 < y < 7:
                g.px(5 + (1 if y < 4 else 0), y, P)             # miolo rosa
        # corpo e anca
        g.ellipse(9.5, 11.5, 4.8, 3.6, W, shade=S, light=B)
        g.ellipse(11.5, 12, 3.0, 3.0, S, shade=D)
        # cabeca
        g.ellipse(5, 9.5, 3.2, 2.7, W, shade=S, light=B)
        g.px(2, 10, B); g.px(3, 11, B)                          # focinho claro
        g.px(4, 8, "r"); g.px(4, 9, "r")                        # olho
        g.px(2, 9, P)                                           # nariz
        # patas e rabo
        g.rect(4, 13, 5, 14, W); g.px(4, 14, B)
        g.rect(9, 14, 13, 15, S); g.rect(9, 14, 11, 14, W)
        g.ellipse(14.2, 10.5, 1.8, 1.8, B)
    elif pose == "crouch":
        for x in range(5, 12):                                  # orelhas deitadas para tras
            g.px(x, 5 + (x - 5) // 4, W if x < 9 else S)
            g.px(x, 6 + (x - 5) // 4, S)
        g.ellipse(9.5, 11.5, 5.2, 3.0, W, shade=S, light=B)
        g.ellipse(12, 12.5, 3.2, 2.6, S, shade=D)
        g.ellipse(4.5, 10.5, 3.0, 2.5, W, shade=S, light=B)
        g.px(3, 9, "r"); g.px(3, 10, "r"); g.px(1, 10, P)
        g.px(2, 11, B)
        g.rect(3, 13, 5, 13, W)
        g.rect(8, 14, 14, 15, S)
        g.ellipse(14.5, 11, 1.7, 1.7, B)
    else:  # air
        for x in range(5, 11):                                  # orelhas ao vento
            g.px(x, 4 + (x - 5) // 3, W if x < 8 else S)
            g.px(x, 5 + (x - 5) // 3, S)
        g.ellipse(8, 8.5, 5.8, 2.6, W, shade=S, light=B)
        g.ellipse(3.5, 7.5, 2.8, 2.3, W, shade=S, light=B)
        g.px(2, 6, "r"); g.px(2, 7, "r"); g.px(0, 7, P)
        g.line(2, 10, 0, 12, W); g.line(3, 10, 1, 13, S)        # patas da frente esticadas
        g.line(11, 10, 15, 12, W); g.line(12, 9, 15, 11, S)     # patas de tras esticadas
        g.ellipse(14, 7, 1.7, 1.7, B)
    g.outline("r")
    return g.lines()


# ================================================================= PASSARO
BIRDS = {
    "yellow": dict(M="o", S="p", W="f", Wd="e", Bk="p", Hi="a"),
    "blue": dict(M="h", S="g", W="q", Wd="g", Bk="o", Hi="i"),
    "red": dict(M="l", S="m", W="m", Wd="b", Bk="o", Hi="p"),
}


def bird(c, pose):
    g = Grid(16, 16)
    M, S, W, Wd, Bk, Hi = c["M"], c["S"], c["W"], c["Wd"], c["Bk"], c["Hi"]
    if pose in ("perch", "perch2"):
        tilt = 1 if pose == "perch2" else 0
        g.ellipse(8, 10, 4.2, 3.4, M, shade=S, light=Hi)             # corpo
        g.ellipse(5.5, 7 + tilt * 0.5, 2.6, 2.4, M, shade=S, light=Hi)  # cabeca
        g.px(3, 7 + tilt, Bk); g.px(2, 7 + tilt, Bk)                 # bico
        g.px(5, 6 + tilt, "r")                                       # olho
        g.rect(8, 9, 11, 11, W)                                      # asa
        g.px(9, 11, Wd); g.px(10, 11, Wd)
        g.rect(12, 11 - tilt, 14, 12 - tilt, W)                      # cauda
        g.px(14, 12 - tilt, Wd)
        g.px(7, 14, Bk); g.px(9, 14, Bk)                             # patinhas
        g.px(7, 13, Bk); g.px(9, 13, Bk)
    else:
        up = pose == "fly"
        g.ellipse(8, 9, 3.8, 2.8, M, shade=S, light=Hi)
        g.ellipse(5, 7.5, 2.3, 2.1, M, shade=S, light=Hi)
        g.px(3, 7, Bk); g.px(2, 7, Bk); g.px(4, 6, "r")
        g.rect(12, 9, 14, 10, W)                                      # cauda
        if up:                                                        # asas para cima
            g.line(8, 7, 11, 1, W); g.line(9, 7, 12, 2, W); g.line(7, 7, 8, 1, Wd)
            g.px(10, 3, Hi)
        else:                                                         # asas para baixo
            g.line(8, 10, 12, 15, W); g.line(9, 10, 13, 14, W); g.line(7, 10, 8, 15, Wd)
    g.outline("r")
    return g.lines()


# ================================================================= PEIXE
FISH = {
    "orange": dict(M="p", S="m", Bl="o", F="l"),
    "blue": dict(M="h", S="g", Bl="i", F="q"),
}


def fish(c, pose):
    g = Grid(16, 16)
    M, S, Bl, F = c["M"], c["S"], c["Bl"], c["F"]
    ang = {"swim": 0.0, "up": -0.9, "peak": 0.0, "down": 0.9}[pose]
    cx, cy = 8, 8
    for i in range(-5, 6):                                   # corpo em fusiforme girado
        t = i / 5.0
        half = 2.8 * math.sqrt(max(0.0, 1 - t * t)) + 0.4
        x = cx + i * math.cos(ang) * -1
        y = cy + i * math.sin(ang) * -1
        for k in range(-int(half), int(half) + 1):
            col = M
            if k > half * 0.4:
                col = Bl
            elif k < -half * 0.45:
                col = S
            g.px(x - k * math.sin(ang), y + k * math.cos(ang), col)
    tx = cx + 6 * math.cos(ang)
    ty = cy + 6 * math.sin(ang)                             # cauda
    for k in (-2, -1, 0, 1, 2):
        g.px(tx + abs(k) * 0.4, ty + k * 0.8, F)
    ex = cx - 3.5 * math.cos(ang) * -1
    g.px(cx - 3 * -math.cos(ang) * -1 - 0, cy - 1, "n")
    g.px(cx - 4 if ang == 0 else cx - 3, cy - 1, "r")
    g.outline("r")
    return g.lines()


# ================================================================= ENGUIA (32x16)
def eel(phase):
    g = Grid(32, 16)
    body = []
    for i in range(0, 25):
        t = i / 24.0
        x = 3 + 24 * t
        y = 8 + 3.2 * math.sin(t * math.pi * 2.2 + phase)
        r = 1.2 + 1.7 * math.sin(min(t * 1.6, 1.0) * math.pi / 2)
        body.append((x, y, r))
    for x, y, r in body:
        g.ellipse(x, y, r, r, "s", shade="q", light="t")
    for x, y, r in body[::3]:                               # barbatana dorsal
        g.px(x, y - r - 1, "u")
    for x, y, r in body[2::4]:                              # barriga clara
        g.px(x, y + r - 0.5, "i")
    hx, hy, hr = body[-1]
    g.ellipse(hx + 2, hy, 3.2, 2.4, "s", shade="q", light="t")
    g.px(hx + 3, hy - 1, "l"); g.px(hx + 3, hy - 0.4, "l")  # olho vermelho
    g.px(hx + 5, hy + 1, "n"); g.px(hx + 4, hy + 1.8, "n")  # dentes
    g.outline("r")
    return g.lines()


# ================================================================= LACAIO (16x24)
def minion(direction, frame):
    g = Grid(16, 24)
    step = 1 if frame == 1 else 0
    # lanca (ao lado)
    for y in range(2, 22):
        g.px(13, y, "e")
    g.rect(12, 0, 14, 2, "d"); g.px(13, 0, "n")
    # corpo (armadura escura)
    g.rect(4, 10, 11, 18, "q")
    g.rect(4, 14, 11, 14, "o")                              # cinto
    g.rect(10, 11, 11, 18, "g")
    g.rect(3, 11, 4, 16, "g"); g.rect(11, 11, 12, 16, "g")  # bracos
    g.px(3, 17, "d"); g.px(12, 17, "d")                     # maos
    # pernas
    g.rect(5, 19, 7, 21 - step, "b"); g.rect(8, 19, 10, 21 - (1 - step), "b")
    g.rect(5, 22 - step, 7, 22 - step, "r"); g.rect(8, 22 - (1 - step), 10, 22 - (1 - step), "r")
    # elmo com crista vermelha
    g.rect(4, 3, 11, 9, "c")
    g.rect(5, 2, 10, 2, "c")
    g.rect(7, 0, 8, 2, "l")
    g.rect(4, 8, 11, 9, "b")
    if direction == "down":
        g.rect(5, 6, 10, 8, "r")                            # viseira escura
        g.px(6, 7, "l"); g.px(9, 7, "l")                    # olhos vermelhos
        g.px(6, 4, "d"); g.px(7, 4, "d")                    # brilho
    else:
        g.px(6, 4, "d"); g.px(7, 4, "d")
    g.outline("r")
    return g.lines()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, c in RABBITS.items():
        save(f"rabbit_{name}", [rabbit(c, p) for p in ("sit", "sit2", "crouch", "air")],
             f"coelho {name} 16x16: sentado, orelha mexendo, agachado, no ar")
    for name, c in BIRDS.items():
        save(f"bird_{name}", [bird(c, p) for p in ("perch", "perch2", "fly", "fly2")],
             f"passaro {name} 16x16: pousado, pousado (inclinado), voando (asas cima/baixo)")
    for name, c in FISH.items():
        save(f"fish_{name}", [fish(c, p) for p in ("swim", "up", "peak", "down")],
             f"peixe {name} 16x16: nadando, subindo, no alto, descendo")
    save("eel", [eel(ph) for ph in (0.0, 1.6, 3.1, 4.7)], "enguia sombria 32x16: 4 quadros de ondulacao")
    save("minion_down", [minion("down", f) for f in (0, 1, 0)], "lacaio da Sombra de frente 16x24")
    save("minion_up", [minion("up", f) for f in (0, 1, 0)], "lacaio da Sombra de costas 16x24")
    print("bichos gerados")


if __name__ == "__main__":
    main()
