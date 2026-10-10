#!/usr/bin/env python3
"""Gera assets/maps/cavernas.* (Cavernas de Quartzo, capitulo 3). Deterministico."""
import json
from pathlib import Path

W, H = 44, 26
ROOT = Path(__file__).resolve().parent.parent / "assets" / "maps"
g = [["W"] * W for _ in range(H)]


def carve(x0, y0, x1, y1, ch="s"):
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            g[y][x] = ch


carve(2, 17, 9, 22)            # sala de entrada
carve(10, 19, 17, 20)          # corredor leste
carve(19, 16, 27, 22)          # sala 2
carve(22, 8, 23, 15)           # corredor norte (2 de largura)
carve(14, 2, 33, 7)            # camara de cristais
carve(34, 4, 36, 5)            # passagem para o portal
g[20][1] = "O"                 # saida (volta a ilha)
carve(18, 19, 18, 20, "x")     # abismo 1: 1 tile
carve(22, 12, 23, 13, "x")     # abismo 2: 2 tiles de profundidade
carve(15, 20, 15, 20, "x")     # buraco extra no corredor (so decorativo: contornavel? nao)
g[20][15] = "s"
g[4][37] = "G"                 # portal do fim do capitulo
g[5][37] = "W"
carve(36, 4, 36, 5)

# cristais nas bordas das salas
for x, y in [(3, 17), (8, 22), (11, 19), (16, 20), (20, 16), (26, 22), (27, 18), (19, 21),
             (14, 2), (16, 2), (19, 2), (24, 2), (28, 2), (31, 2), (33, 3), (14, 6), (18, 7), (30, 7), (21, 9)]:
    if g[y][x] == "s":
        g[y][x] = "q"

(ROOT / "cavernas.map.txt").write_text(
    "; cavernas de quartzo. W parede  s piso  x abismo  q cristal  O saida  G portal\n"
    + "\n".join("".join(r) for r in g) + "\n", encoding="utf-8")

objects = [
    {"kind": "npc", "tile": [24, 4], "name": "Lana", "sprite": "lana", "gives": "pink_car",
     "lines": ["Isabela! Que bom que o unicórnio trouxe você até aqui. Eu sou a Lana.",
               "Eu estudo as pedras brilhantes destas cavernas, o quartzo. Com ele eu construí o terceiro aliado: o Carro Rosa.",
               "O vilão está deixando o castelo cada vez mais escuro, e o tempo está acabando. Com o carro você chega lá a tempo.",
               "Ele só anda em estradas de terra. Escolha o carro no inventário quando estiver na estrada."],
     "after": ["Siga pela passagem brilhante, Isabela. A estrada do pôr do sol está logo depois!"]},
    {"kind": "npc", "tile": [6, 19], "name": "Bruce", "sprite": "bruce",
     "lines": ["Au! Eu sou o Bruce e moro nesta caverna há anos. Estes cristais iluminam o caminho.",
               "Cuidado com os buracos: só o unicórnio consegue pular. Sem ele, volte e escolha o unicórnio no inventário."],
     "after": ["A Lana está lá no fundo, na sala dos cristais."]},
    {"kind": "sign", "tile": [4, 18], "name": "Placa",
     "lines": ["Cavernas de Quartzo. Os buracos só podem ser pulados com o unicórnio."]},
]
(ROOT / "cavernas.objects.json").write_text(json.dumps(objects, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "cavernas.decor.json").write_text("[]\n")
(ROOT / "cavernas.creatures.json").write_text("[]\n")
print("cavernas geradas")
