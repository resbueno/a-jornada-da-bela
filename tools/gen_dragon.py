#!/usr/bin/env python3
"""Gera o Dragao Ancestral (48x32, neon, sinuoso) em art/src/dragon.sprite.txt."""
import math
from pathlib import Path

W, H = 48, 32
OUT = Path(__file__).resolve().parent.parent / "art" / "src" / "dragon.sprite.txt"
g = [["."] * W for _ in range(H)]


def px(x, y, c):
    x, y = int(round(x)), int(round(y))
    if 0 <= x < W and 0 <= y < H:
        g[y][x] = c


LIGHT = {"t": "n", "p": "o", "o": "a", "4": "n", "v": "i", "s": "t"}
DARK = {"t": "u", "p": "m", "o": "p", "4": "2", "v": "g", "s": "q"}


def ball(cx, cy, r, c, shade=True):
    for y in range(int(cy - r) - 1, int(cy + r) + 2):
        for x in range(int(cx - r) - 1, int(cx + r) + 2):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                col = c
                if shade:
                    if y - cy < -r * 0.38 and x - cx < r * 0.4:
                        col = LIGHT[c]
                    elif y - cy > r * 0.42:
                        col = DARK[c]
                px(x, y, col)


palette = ["t", "p", "o", "4", "v", "s"]
N = 90
pts = []
for i in range(N + 1):
    t = i / N
    x = 4 + 33 * t
    y = 20 + 7.5 * math.sin(t * math.pi * 2.1 + 0.5)
    r = 1.7 + 3.3 * math.sin(min(t * 1.25, 1.0) * math.pi / 2)
    pts.append((x, y, r, palette[min(int(t * len(palette)), len(palette) - 1)], t))
# cristas / nadadeiras nas costas (atras do corpo)
for x, y, r, c, t in pts[::7]:
    for k in range(3):
        px(x - 1 + k, y - r - 1 - (1 if k == 1 else 0), "v" if int(t * 20) % 2 else "t")
for x, y, r, c, t in pts:
    ball(x, y, r, c)
# cabeca: focinho alongado, chifres, bigodes e olho
hx, hy = pts[-1][0] + 3, pts[-1][1] - 1
ball(hx, hy, 5.4, "o")
ball(hx + 4.5, hy + 1.3, 3.0, "p")
for k in range(4):                                    # chifres
    px(hx - 2 - k * 0.5, hy - 6 - k, "o"); px(hx - 1 - k * 0.5, hy - 6 - k, "p")
px(hx + 7, hy + 3, "n"); px(hx + 5, hy + 3, "n")      # dentes
px(hx + 8, hy, "r")                                    # narina
px(hx + 1, hy - 1, "n"); px(hx + 2, hy - 1, "n"); px(hx + 2, hy, "r")   # olho
for k in range(7):                                     # bigodes ondulados
    px(hx + 4 + k, hy + 5 + math.sin(k) * 1.0, "n")
for k in range(5):                                     # juba
    px(hx - 4 - k, hy - 3 + k * 0.7, "v" if k % 2 else "t")
# contorno
src = [r[:] for r in g]
for y in range(H):
    for x in range(W):
        if src[y][x] == ".":
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and src[ny][nx] != ".":
                    g[y][x] = "r"
                    break
OUT.write_text("# Dragao Ancestral 48x32 (neon)\n" + "\n".join("".join(r) for r in g) + "\n")
print("dragao gerado")
