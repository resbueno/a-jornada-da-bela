#!/usr/bin/env python3
"""Gera assets/maps/floresta_inicial.* (96x64). Deterministico (seed fixa).

Arvores sao sempre blocos 2x2 alinhados a coordenadas pares (o pinheiro grande ocupa 2x2 tiles).
A regiao original (lago, ilha, vilarejo, trilhas, clareira) mantem as mesmas coordenadas; o mundo
cresceu para o leste e o sul, com mais trilhas, um lago, ruinas, campos de grama alta e pedreira.
"""
import json
import random
from pathlib import Path

W, H = 96, 64
ROOT = Path(__file__).resolve().parent.parent / "assets" / "maps"
OUT = ROOT / "floresta_inicial.map.txt"
rng = random.Random(20261009)

g = [["g"] * W for _ in range(H)]


def rect(x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            g[y][x] = ch


# --- regiao original (mesmas coordenadas) ----------------------------------------
rect(28, 2, 45, 11, "~")            # Grande Lago
rect(37, 3, 43, 6, "g")             # ilha
rect(37, 3, 38, 3, "s"); rect(42, 3, 43, 3, "s")
rect(39, 3, 41, 3, "E")             # entrada da Caverna de Quartzo
rect(37, 4, 43, 4, "x")             # fenda que so o unicornio salta
rect(14, 4, 22, 8, "h")             # grama alta (norte)
rect(26, 18, 40, 24, "h")           # grama alta (sul)
rect(3, 22, 12, 29, "s")            # clareira de pedra
rect(2, 15, 45, 16, "d")            # trilha principal (comeco)
rect(23, 17, 24, 28, "d")           # ramal sul
rect(8, 8, 9, 14, "d")              # ramal norte

# --- regiao nova: trilhas -----------------------------------------------------------
rect(46, 15, 93, 16, "d")           # trilha principal ate o leste
rect(23, 29, 24, 46, "d")           # ramal sul continua ate a estrada do sul
rect(2, 46, 93, 47, "d")            # estrada do sul
rect(60, 17, 61, 45, "d")           # ligacao norte-sul
rect(76, 5, 77, 14, "d")            # trilha para as ruinas
rect(12, 48, 13, 56, "d")           # trilha da pedreira
# --- regiao nova: paisagens ---------------------------------------------------------
rect(66, 24, 82, 38, "~")           # Lago da Lua (decorativo)
rect(72, 29, 76, 33, "g")           # ilhota
rect(70, 3, 92, 12, "s")            # ruinas (piso de pedra)
rect(30, 34, 50, 44, "h")           # campo de grama alta
rect(8, 34, 22, 42, "h")
rect(62, 50, 90, 60, "h")
rect(6, 50, 20, 60, "s")            # pedreira
rect(48, 20, 56, 30, "h")

# --- zonas onde NAO pode nascer arvore/pedra ----------------------------------------
reserved = set()


def reserve(x0, y0, x1, y1):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            reserved.add((x, y))


reserve(26, 0, 47, 12)              # lago + margem + ilha
reserve(1, 14, 94, 17)              # trilha principal
reserve(21, 17, 26, 48)             # ramal sul
reserve(1, 45, 94, 48)              # estrada do sul
reserve(58, 17, 63, 46)             # ligacao norte-sul
reserve(74, 4, 79, 14)              # trilha das ruinas
reserve(10, 47, 15, 57)             # trilha da pedreira
reserve(6, 6, 11, 14)               # ramal norte
reserve(14, 4, 22, 8)
reserve(25, 17, 41, 25)
reserve(30, 34, 50, 44)
reserve(8, 34, 22, 42)
reserve(62, 50, 90, 60)
reserve(48, 20, 56, 30)
reserve(64, 22, 84, 40)             # Lago da Lua
reserve(69, 2, 93, 13)              # ruinas
reserve(5, 49, 21, 61)              # pedreira
reserve(2, 21, 13, 30)              # clareira de pedra
SPOTS = [(24, 15), (29, 12), (38, 5), (26, 14), (32, 13),                          # inicio, NPCs, placas
         (6, 8), (16, 11), (38, 13), (27, 9), (10, 20), (30, 28), (18, 6),         # decorativos
         (36, 6), (40, 8), (33, 10), (10, 7), (12, 14), (30, 14), (42, 5)]         # remo, Teo, Jhonny, Rui
for tx, ty in SPOTS:
    reserve(tx - 1, ty - 1, tx + 1, ty + 1)
for tx, ty in [(48, 14), (25, 44), (59, 14), (75, 15), (14, 48)]:                  # placas novas
    reserve(tx - 1, ty - 1, tx + 1, ty + 1)


def free_block(bx, by):
    for y in (by, by + 1):
        for x in (bx, bx + 1):
            if not (0 <= x < W and 0 <= y < H) or (x, y) in reserved or g[y][x] != "g":
                return False
    return True


def tree(bx, by):
    rect(bx, by, bx + 1, by + 1, "#")


# --- moldura: 2 tiles de floresta + bordas irregulares --------------------------------
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

# --- bosques: centros em grade com variacao --------------------------------------------
centers = []
for cx in range(5, W - 4, 11):
    for cy in range(5, H - 4, 9):
        centers.append((cx + rng.randint(-3, 3), cy + rng.randint(-3, 3)))
for cx, cy in centers:
    for _ in range(40):
        bx = (cx + rng.randint(-6, 6)) // 2 * 2
        by = (cy + rng.randint(-5, 5)) // 2 * 2
        if free_block(bx, by) and rng.random() < 0.8:
            tree(bx, by)

# --- pedras soltas -----------------------------------------------------------------------
placed = tries = 0
while placed < 70 and tries < 2000:
    tries += 1
    x, y = rng.randint(2, W - 3), rng.randint(2, H - 3)
    if (x, y) in reserved or g[y][x] != "g":
        continue
    g[y][x] = "r"
    placed += 1
for x, y in [(3, 21), (6, 21), (11, 21), (13, 24), (13, 28), (2, 26),             # clareira original
             (71, 2), (80, 13), (90, 13), (8, 49), (18, 49), (20, 56), (7, 58)]:    # ruinas e pedreira
    if g[y][x] in "gs":
        g[y][x] = "r"

OUT.write_text(
    "; floresta inicial 96x64. g chao  h grama alta  d trilha  s pedra(piso)  ~ agua  # pinheiro (2x2)  "
    "r pedra grande  E entrada da caverna  x fenda\n"
    + "\n".join("".join(r) for r in g) + "\n",
    encoding="utf-8",
)

# --- decorativos novos (aves, animais, peixes, arco-iris) -------------------------------
base = [
    {"kind": "rainbow", "tile": [6, 8]}, {"kind": "bird", "tile": [16, 11]}, {"kind": "bird", "tile": [38, 13]},
    {"kind": "bird", "tile": [27, 9]}, {"kind": "animal", "tile": [10, 20]}, {"kind": "animal", "tile": [30, 28]},
    {"kind": "animal", "tile": [18, 6]}, {"kind": "fish", "tile": [36, 6]}, {"kind": "fish", "tile": [40, 8]},
    {"kind": "fish", "tile": [33, 10]},
]
drng = random.Random(777)
decor = list(base)


def free_grass(x0, y0, x1, y1):
    for _ in range(400):
        x, y = drng.randint(x0, x1), drng.randint(y0, y1)
        if g[y][x] == "g" and (x, y) not in {(d["tile"][0], d["tile"][1]) for d in decor}:
            return [x, y]
    return None


def free_water(x0, y0, x1, y1):
    for _ in range(400):
        x, y = drng.randint(x0, x1), drng.randint(y0, y1)
        if g[y][x] == "~":
            return [x, y]
    return None


for kind, n, box in (("bird", 8, (48, 4, 92, 60)), ("animal", 7, (50, 18, 92, 60)),
                     ("bird", 4, (4, 30, 46, 60)), ("animal", 4, (4, 30, 46, 60))):
    for _ in range(n):
        t = free_grass(*box)
        if t:
            decor.append({"kind": kind, "tile": t})
for _ in range(7):
    t = free_water(66, 24, 82, 38)
    if t:
        decor.append({"kind": "fish", "tile": t})
decor.append({"kind": "rainbow", "tile": [84, 15]})
decor.append({"kind": "rainbow", "tile": [40, 52]})
(ROOT / "floresta_inicial.decor.json").write_text(json.dumps(decor, indent=1) + "\n")

# --- placas novas -------------------------------------------------------------------------
objs_path = ROOT / "floresta_inicial.objects.json"
objs = json.loads(objs_path.read_text(encoding="utf-8"))
objs = [o for o in objs if not o.get("auto")]
for tile, text in (
    ((48, 14), "Leste: o Lago da Lua e as Ruínas Antigas, no fim da trilha do norte."),
    ((25, 44), "Sul: a estrada do sul, a pedreira e os campos de grama alta."),
    ((59, 14), "Esta trilha desce até a estrada do sul. Cuidado com a grama alta!"),
    ((75, 15), "Ruínas Antigas. Dizem que aqui havia um castelo menor, muito antes do reino."),
    ((14, 48), "Pedreira. As pedras daqui construíram as muralhas do castelo."),
):
    objs.append({"kind": "sign", "tile": list(tile), "name": "Placa", "lines": [text], "auto": True})
objs_path.write_text(json.dumps(objs, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("mapa gerado:", OUT, f"({W}x{H})")
print("arvores:", sum(r.count('#') for r in g), "| pedras:", sum(r.count('r') for r in g),
      "| decorativos:", len(decor), "| placas novas: 5")
