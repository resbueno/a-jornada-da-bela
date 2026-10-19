#!/usr/bin/env python3
"""Gera os objetos grandes do cenario (grade base; o build amplia 2x) em art/src/.

maria_fumaca : locomotiva a vapor classica, de lado (olha para a esquerda), 80x48 na base.
               Quadros: rodas em 2 posicoes.
dragon_sleep : dragao imenso, escamoso e fofo, enrolado e dormindo, visto de cima, 96x64.
               Quadros: respirando (2) e de olhos abertos (1).
Uso: python3 tools/gen_props.py   (depois: tools/build_sprites.py)
"""
import math

import pixel


def train(frame):
    g = pixel.Grid(80, 48)
    # rodas grandes vermelhas com raios (giram entre os quadros)
    wheels = [(20, 38, 7), (38, 38, 7), (56, 38, 7)]
    g.rect(6, 30, 72, 33, "r")                                 # chassi
    g.rect(6, 30, 72, 30, "q")
    for cx, cy, r in wheels:
        g.ellipse(cx, cy, r + 0.5, r + 0.5, "r")
        g.ellipse(cx, cy, r - 0.5, r - 0.5, "l")
        g.ellipse(cx, cy, r - 2.5, r - 2.5, "m")
        for k in range(4):
            a = k * math.pi / 4 + frame * math.pi / 8
            g.line(round(cx - math.cos(a) * (r - 1)), round(cy - math.sin(a) * (r - 1)),
                   round(cx + math.cos(a) * (r - 1)), round(cy + math.sin(a) * (r - 1)), "l")
        g.rect(cx - 1, cy - 1, cx, cy, "o")
    g.ellipse(70, 41, 4, 4, "l"); g.ellipse(70, 41, 2, 2, "m")    # rodinha de tras
    rod_y = 38 + (2 if frame else -2)
    g.line(20, rod_y, 56, rod_y, "d", 2)                       # biela
    # caldeira preta com faixas douradas
    g.rect(8, 16, 52, 29, "r")
    g.rect(8, 16, 52, 18, "q")                                 # brilho de cima
    for x in (16, 30, 44):
        g.rect(x, 16, x + 1, 29, "o")
    g.ellipse(8, 22, 3, 7, "c")                                # frente da caldeira
    g.ellipse(7, 22, 1.5, 2, "a")                              # farol
    g.px(6, 21, "n")
    # chamine em funil e domo dourado
    g.rect(12, 6, 17, 15, "r"); g.rect(10, 3, 19, 6, "r"); g.rect(11, 3, 18, 3, "q")
    g.rect(13, 7, 13, 14, "q")
    g.ellipse(32, 14, 5, 3, "o"); g.rect(28, 14, 36, 16, "o"); g.px(30, 12, "a")
    g.rect(42, 11, 44, 15, "d"); g.px(43, 10, "n")             # apito
    # cabine vermelha com janela (as meninas aparecem ai na cena)
    g.rect(52, 6, 72, 29, "l")
    g.rect(50, 4, 74, 7, "m")                                  # telhado
    g.rect(55, 10, 69, 19, "r"); g.rect(56, 11, 68, 18, "i")   # janela
    g.rect(62, 11, 62, 18, "c")
    g.rect(52, 22, 72, 22, "o")
    # limpa-trilhos na frente
    for k in range(6):
        g.rect(1 + k, 28 + k // 2, 8, 28 + k // 2, "m")
    g.rect(1, 31, 8, 33, "m")
    g.outline(pixel.OUTLINE)
    return g


def dragon(frame):
    """Dragao enrolado dormindo (visto de cima). frame 0/1: respira; 2: olhos abertos."""
    g = pixel.Grid(96, 64)
    breath = 1 if frame == 1 else 0
    # rabo enrolado em volta do corpo (circulos cada vez menores)
    for i in range(46):
        u = i / 45
        a = -0.4 + u * 4.2
        r = 26 + 4 * u
        cx = 52 + math.cos(a) * r * 1.25
        cy = 36 + math.sin(a) * r * 0.62
        rad = 7.5 - u * 5
        g.ellipse(cx, cy, rad, rad * 0.9, "s")
        if i % 5 == 2 and u < 0.9:                             # espinhos rosados no rabo
            g.ellipse(cx, cy - rad * 0.6, 1.6, 1.6, "t")
    tip_a = -0.4 + 4.2
    tx, ty = 52 + math.cos(tip_a) * 30 * 1.25, 36 + math.sin(tip_a) * 30 * 0.62
    g.ellipse(tx, ty, 3, 3, "t")                               # ponta do rabo em coracao
    # corpo
    g.ellipse(54, 34, 26 + breath, 17 + breath, "s")
    g.ellipse(56, 38, 19 + breath, 10, "t")                    # barriga rosa
    for k in range(-14, 16, 5):                                # faixas da barriga
        g.rect(56 + k, 33, 56 + k, 46, "u")
    # escamas
    for y in range(18, 52, 4):
        for x in range(30, 80, 6):
            if g.get(x, y) == "s":
                g.px(x + (y // 4) % 2 * 3, y, "q")
    # asinhas dobradas
    g.ellipse(48, 22, 9, 6, "u"); g.ellipse(64, 21, 9, 6, "u")
    g.line(42, 22, 55, 19, "t"); g.line(58, 19, 71, 22, "t")
    # espinhos fofos ao longo das costas
    for x in range(36, 78, 6):
        g.ellipse(x, 18 + abs(x - 56) // 7, 2.2, 2.2, "t")
    # cabeca apoiada nas patas da frente
    g.ellipse(20, 36, 15, 12, "s")
    g.ellipse(9, 39, 8, 7, "s")                                # focinho
    g.ellipse(8, 41, 5, 3.5, "t")
    g.px(4, 39, "r"); g.px(8, 38, "r")                         # narinas
    g.ellipse(24, 47, 6, 3, "s"); g.ellipse(12, 49, 6, 3, "s") # patinhas
    for x in (9, 12, 15, 21, 24, 27):
        g.px(x, 50 if x < 18 else 48, "n")                     # unhas
    # juba fofa (nuvenzinhas brancas) e chifres
    for cx, cy, r in ((24, 25, 5), (30, 28, 4.5), (18, 24, 4), (33, 34, 4), (31, 40, 4)):
        g.ellipse(cx, cy, r, r, "n")
        g.ellipse(cx - 1, cy - 1, r * 0.5, r * 0.5, "i")
    g.line(18, 26, 12, 17, "a", 2); g.line(25, 25, 25, 15, "a", 2)
    g.px(12, 16, "n"); g.px(25, 14, "n")
    # olhos
    if frame == 2:
        for ex in (14, 22):
            g.ellipse(ex, 33, 2.5, 2.5, "r"); g.px(ex - 1, 32, "n")
    else:
        for ex in (14, 22):                                    # olhos fechados: arquinhos
            g.rect(ex - 2, 33, ex + 2, 33, "r"); g.px(ex - 3, 32, "r"); g.px(ex + 3, 32, "r")
        g.rect(9, 36, 10, 36, "u"); g.rect(24, 37, 25, 37, "u")  # bochechas
    g.outline(pixel.OUTLINE)
    return g


def main():
    pixel.save("maria_fumaca", [train(f) for f in range(2)],
               "Maria Fumaca de lado: rodas em 2 posicoes (grade base 80x48)", hd_ready=False)
    pixel.save("dragon_sleep", [dragon(f) for f in range(3)],
               "dragao dormindo visto de cima: respira (2) e olhos abertos (grade base 96x64)", hd_ready=False)
    print("gerado: maria_fumaca, dragon_sleep")


if __name__ == "__main__":
    main()
