#!/usr/bin/env python3
"""Gera assets/maps/estrada.* (capitulo 4) e portoes.* (climax). Deterministico."""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "assets" / "maps"
rng = random.Random(4004)


def grid(w, h, ch):
    return [[ch] * w for _ in range(h)]


def rect(g, x0, y0, x1, y1, ch):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            g[y][x] = ch


def tree(g, bx, by):
    rect(g, bx, by, bx + 1, by + 1, "#")


def save(name, g, legend, objects, creatures=None, decor=None):
    (ROOT / f"{name}.map.txt").write_text(
        f"; {legend}\n" + "\n".join("".join(r) for r in g) + "\n", encoding="utf-8")
    for suffix, data in (("objects", objects), ("creatures", creatures or []), ("decor", decor or [])):
        (ROOT / f"{name}.{suffix}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


# ======================= ESTRADA DO POR DO SOL (150x22) =======================
W, H = 150, 22
g = grid(W, H, "g")
rect(g, 0, 0, W - 1, 3, "~")                    # mar
for x in range(0, W, 6):                         # rochedos no mar
    g[rng.randint(1, 3)][x + rng.randint(0, 3) % 6 if x + 3 < W else x] = "r"
rect(g, 0, 7, 133, 13, "d")                      # estrada (7 faixas)
rect(g, 134, 7, 149, 13, "g")                    # acampamento
rect(g, 0, 18, W - 1, H - 1, "#")                # floresta ao sul
for bx in range(0, W, 2):                        # irregularidade da copa
    if rng.random() < 0.35:
        tree(g, bx, 16)
for bx in range(0, W - 4, 2):                    # arvores entre mar e estrada
    if rng.random() < 0.22:
        tree(g, bx, 4)
# obstaculos: blocos de pedras na estrada, sempre deixando uma passagem
patterns = [(7, 10), (10, 13), (8, 11), (9, 12)]
creatures = []
for k, c in enumerate(range(14, 128, 9)):
    a, b = patterns[k % len(patterns)]
    rect(g, c, a, c, b, "r")
    if k % 2 == 1:                               # lacaio patrulha a pista entre os obstaculos
        creatures.append({"kind": "minion", "tile": [c + 4, 10], "range": [8, 12]})
# acampamento
for x, y in [(138, 8), (142, 8), (138, 12), (142, 12), (146, 8), (146, 12)]:
    g[y][x] = "T"
g[10][149] = "G"
rect(g, 148, 9, 148, 11, "g")
objects = [
    {"kind": "sign", "tile": [4, 8], "name": "Placa",
     "lines": ["Estrada do Pôr do Sol! Abra o inventário (tecla I) e escolha o Carro Rosa quando estiver na estrada.",
               "Desvie das pedras e dos soldados da Sombra. Chegue ao acampamento antes que a barra de tempo acabe!"]},
    {"kind": "sign", "tile": [136, 10], "name": "Placa",
     "lines": ["Acampamento da Resistência. O carro só anda na estrada: continue a pé até a Princesa Sara."]},
    {"kind": "npc", "tile": [144, 10], "name": "Sara", "sprite": "sara", "gives": "dragon",
     "lines": ["Isabela! Você chegou a tempo. Eu sou a Sara e cuido do último aliado: o Dragão.",
               "Ele é grande, colorido e muito alegre. Vai nos ajudar a derrubar a cerca de espinhos do castelo.",
               "Venha comigo até os portões. Lá as cinco princesas vão se reunir ao redor do altar."],
     "after": ["O castelo está logo ali. Vamos libertar o reino, Isabela!"]},
]
save("estrada", g,
     "estrada do por do sol. d estrada  g chao  ~ mar  r pedra  # arvore  T barraca  G portal",
     objects, creatures)

# ======================= PORTOES DO CASTELO (36x24) =======================
W, H = 36, 24
g = grid(W, H, "g")
rect(g, 0, 0, W - 1, 1, "#")
rect(g, 0, 0, 1, H - 1, "#")
rect(g, W - 2, 0, W - 1, H - 1, "#")
rect(g, 0, H - 2, W - 1, H - 1, "#")
rect(g, 10, 2, 25, 7, "K")                       # muralha
rect(g, 16, 5, 19, 7, "Y")                       # barreira de espinhos magicos
rect(g, 17, 8, 18, 22, "d")                      # caminho ate o altar
rect(g, 14, 11, 21, 14, "d")                     # praca do altar
for bx, by in [(2, 4), (4, 8), (2, 14), (4, 18), (30, 4), (28, 9), (31, 14), (28, 18), (6, 2), (26, 2), (8, 20), (24, 20)]:
    if g[by][bx] == "g":
        tree(g, bx, by)
objects = [
    {"kind": "altar", "tile": [18, 12], "name": "Altar", "lines": [""]},
    {"kind": "npc", "tile": [15, 13], "name": "Olívia", "sprite": "olivia",
     "lines": ["O barco está pronto, Isabela."]},
    {"kind": "npc", "tile": [21, 13], "name": "Lara", "sprite": "lara",
     "lines": ["O unicórnio está esperando."]},
    {"kind": "npc", "tile": [16, 15], "name": "Lana", "sprite": "lana",
     "lines": ["O carro rosa está brilhando."]},
    {"kind": "npc", "tile": [20, 15], "name": "Sara", "sprite": "sara",
     "lines": ["Quando os quatro aliados estiverem no altar, o dragão vai acordar.", "Toque no altar, Isabela!"]},
]
save("portoes", g,
     "portoes do castelo. # arvore  K muralha  Y espinhos  d caminho  g chao",
     objects)
print("estrada e portoes gerados")
