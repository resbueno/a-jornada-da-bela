#!/usr/bin/env python3
"""Gera os veiculos (32x32) como grades de caracteres em art/src/.

Vistas: side (olha para a esquerda; a direita e espelho), front (para baixo), back (para cima).
2 frames por vista (balanco / galope / roda). A Isabela e composta por cima no jogo
(src/sprites.py: RIDER), entao aqui o veiculo deixa transparente o lugar dela.
Uso: python3 tools/gen_vehicles.py   (depois: build_sprites.py art/src assets/sprites)
"""
from pathlib import Path

W = H = 32
OUT = Path(__file__).resolve().parent.parent / "art" / "src"


class Grid:
    def __init__(self):
        self.g = [["."] * W for _ in range(H)]

    def px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            self.g[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(H):
            for x in range(W):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                    self.px(x, y, c)

    def outline(self, color="r"):
        src = [row[:] for row in self.g]
        for y in range(H):
            for x in range(W):
                if src[y][x] != ".":
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and src[ny][nx] != ".":
                        self.g[y][x] = color
                        break

    def lines(self):
        return ["".join(r) for r in self.g]


# --------------------------------------------------------------- barco
def boat_side(frame):
    g = Grid()
    bob = frame  # sobe/desce 1 px
    # ondas
    for x in range(2, 30):
        if (x + frame * 2) % 4 < 2:
            g.px(x, 30 + 0, "i")
    # casco
    y0 = 22 + bob
    g.rect(4, y0 + 2, 27, y0 + 6, "f")
    g.rect(2, y0, 5, y0 + 3, "f")           # proa levantada
    g.rect(26, y0, 29, y0 + 3, "f")         # popa
    g.rect(5, y0 + 6, 26, y0 + 7, "e")      # quilha
    g.rect(4, y0 + 3, 27, y0 + 3, "e")      # borda interna
    for x in range(6, 26, 5):
        g.px(x, y0 + 4, "e")
        g.px(x, y0 + 5, "e")
    g.px(3, y0, "a"); g.px(28, y0, "a")      # ponteiras claras
    g.rect(2, y0 + 2, 3, y0 + 2, "o")        # fita dourada na proa
    g.outline("r")
    return g.lines()


def boat_front(frame, back=False):
    g = Grid()
    for x in range(8, 24):
        if (x + frame * 2) % 4 < 2:
            g.px(x, 30, "i")
    y0 = 22 + frame
    g.rect(9, y0, 22, y0 + 3, "f")
    g.rect(9, y0, 22, y0, "e")
    g.rect(10, y0 + 4, 21, y0 + 5, "f")
    g.rect(12, y0 + 6, 19, y0 + 7, "e")
    if back:
        g.rect(11, y0 + 1, 20, y0 + 1, "e")
    else:
        g.px(15, y0 + 1, "o"); g.px(16, y0 + 1, "o")  # figura de proa
        g.rect(14, y0 - 1, 17, y0, "a")
    g.outline("r")
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
    g.outline("r")
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
    g.outline("r")
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
    g.outline("r")
    return g.lines()


# --------------------------------------------------------------- carro rosa
def car_side(frame):
    g = Grid()
    g.rect(3, 21, 28, 27, "t")               # carroceria
    g.rect(3, 25, 28, 27, "u")
    g.rect(4, 20, 9, 20, "t")                # capo
    g.rect(21, 20, 27, 20, "t")
    g.rect(10, 20, 20, 21, "u")              # interior (banco)
    g.rect(3, 22, 4, 24, "o")                # farol
    g.rect(27, 22, 28, 23, "l")              # lanterna
    g.rect(2, 26, 29, 26, "n")               # parachoques
    for wx in (9, 23):                        # rodas
        g.ellipse(wx, 28, 3.4, 3.4, "r")
        g.px(wx, 28, "d")
        g.px(wx + (frame * 2 - 1), 28 + (frame * 2 - 1), "n")
    g.rect(14, 18, 14, 20, "d")              # para-brisa
    g.px(15, 18, "i"); g.px(15, 19, "i")
    g.outline("r")
    return g.lines()


def car_front(frame, back=False):
    g = Grid()
    g.rect(7, 22, 24, 28, "t")
    g.rect(7, 26, 24, 28, "u")
    g.rect(8, 20, 23, 21, "d")               # para-brisa / vidro
    g.rect(9, 20, 22, 20, "i")
    g.rect(6, 29, 25, 29, "n")
    for wx in (6, 24):
        g.rect(wx - 1, 25, wx + 1, 30, "r")
        g.px(wx, 27 + frame, "d")
    if back:
        g.rect(9, 24, 11, 25, "l"); g.rect(20, 24, 22, 25, "l")
        g.rect(14, 24, 17, 25, "n")
    else:
        g.rect(9, 24, 11, 25, "o"); g.rect(20, 24, 22, 25, "o")
        g.rect(14, 24, 17, 25, "n")
    g.outline("r")
    return g.lines()


VEHICLES = {
    "boat":     {"side": boat_side, "front": lambda f: boat_front(f), "back": lambda f: boat_front(f, True)},
    "unicorn":  {"side": unicorn_side, "front": unicorn_front, "back": unicorn_back},
    "pink_car": {"side": car_side, "front": lambda f: car_front(f), "back": lambda f: car_front(f, True)},
}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, views in VEHICLES.items():
        for view, fn in views.items():
            frames = [fn(f) for f in range(2)]
            body = "\n---\n".join("\n".join(fr) for fr in frames)
            (OUT / f"vehicle_{name}_{view}.sprite.txt").write_text(
                f"# {name} vista {view} (32x32): 2 frames\n{body}\n", encoding="utf-8")
        print("gerado:", name)


if __name__ == "__main__":
    main()
