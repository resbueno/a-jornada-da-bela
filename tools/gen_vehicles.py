#!/usr/bin/env python3
"""Gera os veiculos como grades de caracteres em art/src/ (grade base; o build amplia 2x).

Barco (48x40 na base): feito de madeira e blocos de montar, com mastro e vela. Unicornio (32x32).
Vistas: side (olha para a esquerda; a direita e espelho), front (para baixo), back (para cima).
2 frames por vista (balanco / galope). A Isabela e as amigas sao compostas por cima no jogo
(src/sprites.py: RIDER), entao aqui o veiculo deixa livre o lugar delas.
Uso: python3 tools/gen_vehicles.py   (depois: tools/build_sprites.py)
"""
from pathlib import Path

import pixel

OUT = Path(__file__).resolve().parent.parent / "art" / "src"
BLOCKS = ("l", "o", "h", "2", "t")          # cores dos blocos de montar


class Grid(pixel.Grid):
    def __init__(self, w=32, h=32):
        super().__init__(w, h)


# --------------------------------------------------------------- barco
def blocks(g, x0, x1, y):
    """Fileira de blocos de montar coloridos (com o pino claro em cima)."""
    for i, x in enumerate(range(x0, x1 - 1, 4)):
        c = BLOCKS[i % len(BLOCKS)]
        g.rect(x, y, x + 2, y + 1, c)
        g.px(x + 1, y - 1, pixel.LIGHT.get(c, c))


def boat_side(frame):
    g = Grid(48, 40)
    for x in range(2, 46):                   # ondas
        if (x + frame * 2) % 5 < 2:
            g.px(x, 39, "i")
    y0 = 28 + frame
    g.rect(4, y0 + 2, 43, y0 + 6, "f")       # casco
    g.rect(1, y0 - 1, 6, y0 + 3, "f")        # proa levantada
    g.rect(40, y0, 45, y0 + 3, "f")          # popa
    g.rect(6, y0 + 7, 41, y0 + 8, "e")       # quilha
    g.rect(4, y0 + 5, 43, y0 + 5, "e")       # tabuas
    for x in range(8, 42, 6):
        g.px(x, y0 + 3, "e"); g.px(x, y0 + 4, "e")
    blocks(g, 7, 40, y0 + 1)
    g.px(2, y0 - 1, "a"); g.rect(1, y0 + 1, 2, y0 + 1, "o")
    g.rect(9, 5, 9, y0, "e")                 # mastro
    g.rect(10, 5, 13, 6, "l")                # bandeirinha
    for y in range(8, y0 - 2):               # vela branca com listras rosa
        w = 1 + (y - 8) * 7 // max(y0 - 10, 1)
        for x in range(10, 10 + w):
            g.px(x, y, "t" if (y // 4) % 2 else "n")
    g.outline(pixel.OUTLINE)
    return g.lines()


def boat_front(frame, back=False):
    g = Grid(48, 40)
    for x in range(10, 38):
        if (x + frame * 2) % 5 < 2:
            g.px(x, 39, "i")
    y0 = 28 + frame
    g.rect(12, y0, 35, y0 + 4, "f")
    g.rect(14, y0 + 5, 33, y0 + 6, "f")
    g.rect(18, y0 + 7, 29, y0 + 8, "e")
    g.rect(12, y0 + 3, 35, y0 + 3, "e")
    blocks(g, 13, 35, y0 + 1)
    if not back:
        g.rect(22, y0 + 4, 25, y0 + 5, "o")  # figura de proa dourada
    g.outline(pixel.OUTLINE)
    return g.lines()


# --------------------------------------------------------------- unicornio
def unicorn_side(frame):
    g = Grid()
    # patas (galope: alterna abertura)
    spread = frame * 2
    for lx, shift in ((8, -spread), (12, spread), (19, -spread), (23, spread)):
        g.rect(lx + shift // 2, 25, lx + shift // 2 + 1, 29, "n")
        g.rect(lx + shift // 2, 30, lx + shift // 2 + 1, 31, "b")
    # corpo
    g.ellipse(16, 22, 11, 5, "n")
    g.rect(8, 24, 24, 26, "a")               # sombra da barriga
    # pescoco e cabeca
    g.rect(5, 12, 9, 20, "n")
    g.rect(1, 12, 6, 16, "n")
    g.px(2, 14, "r")                         # olho
    g.rect(1, 16, 2, 16, "t")                # focinho rosado
    g.rect(2, 8, 2, 11, "o")                 # chifre
    g.px(2, 7, "o"); g.px(3, 9, "p")
    # crina e cauda roxas
    g.rect(6, 10, 9, 21, "s")
    g.rect(7, 12, 8, 19, "t")
    g.rect(24, 19, 29, 28, "s")
    g.rect(26, 20, 28, 27, "t")
    g.outline(pixel.OUTLINE)
    return g.lines()


def unicorn_front(frame):
    g = Grid()
    g.rect(9, 17, 22, 25, "n")                # peito
    g.rect(9, 22, 22, 25, "a")
    g.rect(11, 26, 12, 31, "n"); g.rect(19, 26, 20, 31, "n")
    g.rect(11, 30, 12, 31, "b"); g.rect(19, 30, 20, 31, "b")
    g.rect(12, 12 + frame, 19, 21 + frame, "n")  # cabeca
    g.rect(14, 20 + frame, 17, 22 + frame, "t")  # focinho
    g.px(13, 17 + frame, "r"); g.px(18, 17 + frame, "r")
    g.rect(15, 7 + frame, 16, 11 + frame, "o")  # chifre
    g.rect(10, 12 + frame, 11, 22 + frame, "s")  # crina
    g.rect(20, 12 + frame, 21, 22 + frame, "s")
    g.outline(pixel.OUTLINE)
    return g.lines()


def unicorn_back(frame):
    g = Grid()
    g.rect(9, 17, 22, 26, "n")
    g.rect(9, 23, 22, 26, "a")
    g.rect(10, 27, 12, 31, "n"); g.rect(19, 27, 21, 31, "n")
    g.rect(10, 30, 12, 31, "b"); g.rect(19, 30, 21, 31, "b")
    g.rect(13, 19, 18, 29, "s")               # cauda
    g.rect(15, 20, 16, 27, "t")
    g.rect(12 + frame, 28, 19 - frame, 29, "s")
    g.outline(pixel.OUTLINE)
    return g.lines()


VEHICLES = {
    "boat":    {"side": boat_side, "front": lambda f: boat_front(f), "back": lambda f: boat_front(f, True)},
    "unicorn": {"side": unicorn_side, "front": unicorn_front, "back": unicorn_back},
}


def main():
    for name, views in VEHICLES.items():
        for view, fn in views.items():
            pixel.save(f"vehicle_{name}_{view}", [fn(f) for f in range(2)],
                       f"{name} vista {view}: 2 frames (grade base)", hd_ready=False)
        print("gerado:", name)


if __name__ == "__main__":
    main()
