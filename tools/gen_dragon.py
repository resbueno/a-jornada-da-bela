#!/usr/bin/env python3
"""Gera o Dragao Ancestral (32x32, cores neon) em art/src/dragon.sprite.txt."""
import math
from pathlib import Path

W = H = 32
OUT = Path(__file__).resolve().parent.parent / "art" / "src" / "dragon.sprite.txt"
g = [["."] * W for _ in range(H)]


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        g[y][x] = c


def disc(cx, cy, r, c):
    for y in range(H):
        for x in range(W):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                px(x, y, c)


# asas (atras do corpo)
for k in range(11):
    px(11 + k, 12 - k // 2, "v"); px(12 + k, 13 - k // 2, "v")
    for j in range(0, 7 - k // 2):
        px(12 + k, 14 - k // 2 + j, "v" if j % 3 else "n")
# corpo serpentino, do rabo (esquerda) a cabeca (direita), cores neon em degrade
palette = ["t", "p", "o", "4", "v", "s"]
N = 60
for i in range(N + 1):
    t = i / N
    x = 3 + 22 * t
    y = 20 + 6 * math.sin(t * math.pi * 2.2)
    r = 1.6 + 2.4 * math.sin(min(t * 1.4, 1.0) * math.pi / 2)
    disc(x, y, r, palette[int(t * (len(palette) - 0.01))])
# cabeca
hx, hy = 26, 17
disc(hx, hy, 4, "o")
disc(hx + 3, hy + 1, 2.2, "p")
px(hx + 1, hy - 1, "n"); px(hx + 2, hy - 1, "r")             # olho
px(hx - 1, hy - 5, "t"); px(hx + 1, hy - 6, "t")               # chifres
px(hx + 4, hy + 2, "n")                                         # dente
# cristas
for i in range(0, N, 6):
    t = i / N
    x = 3 + 22 * t
    y = 20 + 6 * math.sin(t * math.pi * 2.2)
    px(round(x), round(y) - 4, "4")
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
OUT.write_text("# Dragao Ancestral 32x32 (neon)\n" + "\n".join("".join(r) for r in g) + "\n")
print("dragao gerado")
