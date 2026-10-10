#!/usr/bin/env python3
"""Gera Tia Dani e Tio Vitor levantando pesos (canvas 16x24) em art/src/.

Tia Dani : pele branca, cabelo preto, faixa rosa na testa, top rosa e legging roxa
Tio Vitor: careca, barba curta, varias tatuagens (azul-escuro), regata vermelha e bermuda azul

3 quadros por vista, em ordem de movimento: barra no peito, barra na testa, barra no alto.
O jogo toca 0-1-2-1. Eles sempre encaram o jogador, entao up/left sao copias de down.
Uso: python3 tools/gen_gym.py   (depois: build_sprites.py art/src assets/sprites)
"""
from pathlib import Path

from gen_characters import Grid

OUT = Path(__file__).resolve().parent.parent / "art" / "src"

BAR_Y = (11, 5, 2)      # altura da barra em cada quadro

PEOPLE = {
    "tia_dani": dict(
        hair="r", hair_hi="q", skin="j", skin_sh="k", band="t", beard=None, bald=False, tattoos=False,
        top="t", top_sh="u", legs="s", legs_sh="q", bare=False, shoes="n", wide=False),
    "tio_vitor": dict(
        hair=None, hair_hi=None, skin="j", skin_sh="k", band=None, beard="b", bald=True, tattoos=True,
        top="l", top_sh="m", legs="q", legs_sh="g", bare=True, shoes="n", wide=True),
}


def figure(c, pose):
    g = Grid()
    ink = "q"
    wide = c["wide"]
    # pernas e tenis
    g.rect(5, 16, 10, 19, c["legs"])
    g.rect(8, 16, 10, 19, c["legs"]); g.rect(10, 16, 10, 19, c["legs_sh"])
    g.px(7, 17, c["legs_sh"]); g.px(7, 18, c["legs_sh"]); g.px(7, 19, c["legs_sh"])
    if c["bare"]:                                           # bermuda curta, pernas de fora
        g.rect(5, 19, 10, 19, c["skin"])
        g.px(7, 19, c["skin_sh"]); g.px(10, 19, c["skin_sh"])
        if c["tattoos"]:
            g.px(5, 19, ink); g.px(9, 19, ink)
    g.rect(5, 20, 7, 21, c["shoes"]); g.rect(8, 20, 10, 21, c["shoes"])
    g.rect(5, 21, 10, 21, "d")
    # tronco
    x0, x1 = (4, 11) if wide else (5, 10)
    g.rect(5, 11, 10, 15, c["top"])
    g.rect(10, 12, 10, 15, c["top_sh"])
    if wide:
        g.rect(4, 11, 4, 12, c["skin"]); g.rect(11, 11, 11, 12, c["skin_sh"])   # ombros de fora
        if c["tattoos"]:
            g.px(5, 11, c["skin"]); g.px(10, 11, c["skin"])                     # alcas da regata
            g.px(7, 11, c["skin"]); g.px(8, 11, c["skin"]); g.px(7, 12, c["skin_sh"]); g.px(8, 12, c["skin_sh"])
            g.px(7, 11, ink); g.px(8, 12, ink)                                  # tatuagem no peito
    else:
        g.rect(5, 14, 10, 15, c["skin"])                                        # barriga de fora
        g.px(10, 14, c["skin_sh"]); g.px(10, 15, c["skin_sh"])
        g.rect(5, 16, 10, 16, c["legs_sh"])                                     # cos da legging
    # bracos
    by = BAR_Y[pose]
    for side in (0, 1):
        def px(x, y, col, side=side):
            g.px(x if side == 0 else 15 - x, y, col)
        sk, sh = c["skin"], c["skin_sh"]
        if pose == 0:                                       # cotovelos para baixo, barra na clavicula
            for y in range(11, 15):
                px(3, y, sk); px(4, y, sh)
        else:
            for y in range(by, 10):                         # antebraco vertical
                px(2, y, sk); px(3, y, sh)
            for y in range(10, 13):                         # braco ate o ombro
                px(3, y, sk); px(4, y, sh)
        if c["tattoos"]:                                    # tatuagens nos bracos
            ys = (12, 14) if pose == 0 else tuple(range(by + 1, 13, 2))
            for y in ys:
                px(3 if pose == 0 else 2, y, ink)
    # barra e anilhas
    g.rect(2, by, 13, by, "d")
    for x0p in (0, 14):
        g.rect(x0p, by - 2, x0p + 1, by + 3, "c")                               # anilha grande: 2x6
        g.rect(x0p, by - 2, x0p + 1, by - 2, "d")
        edge = x0p if x0p == 0 else x0p + 1
        g.rect(edge, by - 1, edge, by + 3, "b")
    hand_y = by
    for x in (2, 3, 12, 13) if pose else (3, 4, 11, 12):
        g.px(x, hand_y, c["skin"] if x in (2, 13, 3, 12) else c["skin_sh"])
    # cabeca
    g.rect(4, 3, 11, 10, c["skin"])
    g.px(4, 3, "."); g.px(11, 3, ".")
    if c["bald"]:
        g.px(6, 3, "n"); g.px(7, 3, "n"); g.px(5, 4, "n")                       # brilho na careca
        g.rect(5, 5, 6, 5, "b"); g.rect(9, 5, 10, 5, "b")                       # sobrancelhas
        if pose == 0:
            g.rect(3, 6, 3, 7, c["skin_sh"]); g.rect(12, 6, 12, 7, c["skin_sh"])   # orelhas
    else:
        g.rect(4, 2, 11, 4, c["hair"])
        g.px(4, 2, "."); g.px(11, 2, ".")
        g.rect(4, 5, 4, 10, c["hair"]); g.rect(11, 5, 11, 10, c["hair"])
        for x in (5, 6, 7, 9, 10):
            g.px(x, 5, c["hair"])
        g.px(6, 2, c["hair_hi"]); g.px(7, 2, c["hair_hi"]); g.px(5, 3, c["hair_hi"])
        g.rect(4, 4, 11, 4, c["band"])                                          # faixa rosa
        g.px(5, 8, "t"); g.px(10, 8, "t")                                       # bochechas coradas
    g.rect(6, 6, 6, 7, "r"); g.rect(9, 6, 9, 7, "r")                            # olhos
    mouth = "m" if pose else c["skin_sh"]                                       # esforco: boca aberta
    g.px(7, 9, mouth); g.px(8, 9, mouth)
    if c["beard"]:                                                              # barba curta
        b = c["beard"]
        g.rect(4, 8, 4, 10, b); g.rect(11, 8, 11, 10, b)
        g.rect(5, 10, 10, 10, b)
        g.rect(5, 9, 6, 9, b); g.rect(9, 9, 10, 9, b)
        g.px(7, 8, b); g.px(8, 8, b)                                            # bigode
        g.px(7, 9, mouth); g.px(8, 9, mouth)
    g.outline("r")
    return g.lines()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, c in PEOPLE.items():
        frames = [figure(c, p) for p in range(3)]
        body = "\n---\n".join("\n".join(fr) for fr in frames)
        for view in ("down", "up", "left"):
            (OUT / f"{name}_{view}.sprite.txt").write_text(
                f"# {name} levantando peso ({view}): peito, testa, alto (16x24)\n{body}\n", encoding="utf-8")
        print("gerado:", name)


if __name__ == "__main__":
    main()
