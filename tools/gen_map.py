#!/usr/bin/env python3
"""Gera assets/maps/floresta_inicial.map.txt (48x32). Deterministico (seed fixa).

Arvores sao sempre blocos 2x2 alinhados a coordenadas pares (o desenho do pinheiro grande
ocupa 2x2 tiles). Zonas reservadas (lago, ilha, trilhas, NPCs, decorativos) ficam livres.
"""
import random
from pathlib import Path

W, H = 48, 32
OUT = Path(__file__).resolve().parent.parent / "assets" / "maps" / "floresta_inicial.map.txt"
rng = random.Random(20261009)

g = [["g"] * W for _ in range(H)]


def rect(x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            g[y][x] = ch


# --- areas fixas ---------------------------------------------------------
rect(28, 2, 45, 11, "~")            # Grande Lago
rect(37, 3, 43, 6, "g")             # ilha
rect(37, 3, 38, 3, "s"); rect(42, 3, 43, 3, "s")   # rocha ao redor da entrada
rect(39, 3, 41, 3, "E")             # entrada da Caverna de Quartzo (fim do capitulo 2)
rect(37, 4, 43, 4, "x")             # fenda que so o unicornio salta
rect(14, 4, 22, 8, "h")             # grama alta (norte)
rect(26, 18, 40, 24, "h")           # grama alta (sul)
rect(3, 22, 12, 29, "s")            # clareira de pedra (entrada da caverna)
rect(2, 15, 45, 16, "d")            # trilha principal
rect(23, 17, 24, 28, "d")           # ramal sul
rect(8, 8, 9, 14, "d")              # ramal norte

# --- zonas onde NAO pode nascer arvore/pedra -------------------------------
reserved = set()


def reserve(x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            reserved.add((x, y))


reserve(26, 0, 47, 12)              # lago + margem + ilha
reserve(1, 14, 46, 17)              # trilha principal e arredores
reserve(21, 17, 26, 29)             # ramal sul
reserve(6, 6, 11, 14)               # ramal norte
reserve(14, 4, 22, 8)               # grama alta norte
reserve(25, 17, 41, 25)             # grama alta sul
reserve(2, 21, 13, 30)              # clareira de pedra
for tx, ty in [(24, 15), (29, 12), (38, 5), (26, 14), (32, 13),                 # inicio, NPCs, placas
               (6, 8), (16, 11), (38, 13), (27, 9), (10, 20), (30, 28), (18, 6),  # decorativos
               (36, 6), (40, 8), (33, 10)]:
    reserve(tx - 1, ty - 1, tx + 1, ty + 1)


def free_block(bx, by):
    """Bloco 2x2 em coordenadas pares livre?"""
    for y in (by, by + 1):
        for x in (bx, bx + 1):
            if not (0 <= x < W and 0 <= y < H) or (x, y) in reserved or g[y][x] != "g":
                return False
    return True


def tree(bx, by):
    rect(bx, by, bx + 1, by + 1, "#")


# --- moldura: 2 tiles de floresta + bordas irregulares ----------------------
for y in range(H):
    for x in range(W):
        if x < 2 or y < 2 or x >= W - 2 or y >= H - 2:
            g[y][x] = "#"
for bx in range(2, W - 2, 2):
    for by in (2, H - 4):
        if free_block(bx, by) and rng.random() < 0.45:
            tree(bx, by)
for by in range(4, H - 4, 2):
    for bx in (2, W - 4):
        if free_block(bx, by) and rng.random() < 0.45:
            tree(bx, by)

# --- bosques internos --------------------------------------------------------
centers = [(8, 4), (30, 26), (42, 28), (44, 20), (12, 11), (36, 14), (18, 24), (4, 18), (20, 12), (44, 14), (30, 4), (16, 28), (46, 8), (10, 18), (34, 28)]
for cx, cy in centers:
    for _ in range(30):
        bx = (cx + rng.randint(-6, 6)) // 2 * 2
        by = (cy + rng.randint(-5, 5)) // 2 * 2
        if free_block(bx, by) and rng.random() < 0.8:
            tree(bx, by)

# --- pedras soltas -------------------------------------------------------------
placed = 0
tries = 0
while placed < 14 and tries < 400:
    tries += 1
    x, y = rng.randint(2, W - 3), rng.randint(2, H - 3)
    if (x, y) in reserved or g[y][x] != "g":
        continue
    g[y][x] = "r"
    placed += 1
# algumas pedras na borda da clareira
for x, y in [(3, 21), (6, 21), (11, 21), (13, 24), (13, 28), (2, 26)]:
    if g[y][x] == "g":
        g[y][x] = "r"

OUT.write_text(
    "; floresta inicial. g chao  h grama alta  d trilha  s pedra(piso)  ~ agua  # pinheiro (2x2)  r pedra grande  C castelo\n"
    + "\n".join("".join(r) for r in g) + "\n",
    encoding="utf-8",
)
print("mapa gerado:", OUT)
trees = sum(row.count("#") for row in g)
print("tiles de arvore:", trees, "| pedras:", sum(row.count("r") for row in g))
