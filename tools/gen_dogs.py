#!/usr/bin/env python3
"""Gera os cachorros do jogo (canvas 16x24, igual aos personagens) em art/src/.

Teo     : spitz alemao (laranja e creme, pelo fofo, orelhas pontudas)
Jhonny  : shih tzu marrom e branco
Lola    : shih tzu marrom e branca, com lacinho rosa (irma do Jhonny)
Bruce   : shih tzu cinza

Vistas: down (frente), up (costas), left (perfil; a direita e espelho).
3 frames por vista: parado e dois com o rabo balancando.
"""
from pathlib import Path

W, H = 16, 24
OUT = Path(__file__).resolve().parent.parent / "art" / "src"

DOGS = {
    "teo": dict(kind="spitz", main="p", light="a", dark="m", spot="n", nose="r", bow=None),
    "jhonny": dict(kind="shih", main="e", light="f", dark="b", spot="n", nose="r", bow=None),
    "lola": dict(kind="shih", main="e", light="f", dark="b", spot="n", nose="r", bow="t"),
    "bruce": dict(kind="shih", main="c", light="d", dark="b", spot="n", nose="r", bow=None),
}


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


def front(d, wag):
    g = Grid()
    spitz = d["kind"] == "spitz"
    # corpo e patas
    g.ellipse(8, 18, 5.2 if spitz else 4.6, 3.8, d["main"])
    g.rect(4, 20, 5, 22, d["main"]); g.rect(10, 20, 11, 22, d["main"])
    g.rect(4, 22, 5, 22, d["spot"]); g.rect(10, 22, 11, 22, d["spot"])        # patinhas brancas
    g.rect(6, 18, 9, 21, d["spot"])                                           # peito branco
    if spitz:
        g.rect(5, 17, 10, 18, d["light"])                                     # gola de pelo
    # cabeca
    g.ellipse(8, 13, 5.2 if spitz else 4.8, 3.9, d["main"])
    g.rect(6, 12, 9, 16, d["spot"])                                           # mascara branca
    if d["kind"] == "shih":
        g.rect(2, 11, 3, 17, d["dark"]); g.rect(12, 11, 13, 17, d["dark"])     # orelhas compridas caidas
        g.px(2, 11, d["main"]); g.px(13, 11, d["main"])
        g.rect(5, 9, 10, 10, d["light"])                                      # topete
    else:
        g.rect(4, 9, 5, 10, d["main"]); g.rect(10, 9, 11, 10, d["main"])       # orelhas pontudas
        g.px(4, 8, d["main"]); g.px(11, 8, d["main"])
        g.px(5, 10, d["light"]); g.px(10, 10, d["light"])
    g.px(6, 13, "r"); g.px(9, 13, "r")                                        # olhos
    g.px(7, 15, d["nose"]); g.px(8, 15, d["nose"])                            # nariz
    if d["bow"]:                                                              # lacinho
        g.px(7, 8, d["bow"]); g.px(8, 8, d["bow"]); g.px(6, 7, d["bow"]); g.px(9, 7, d["bow"])
        g.px(7, 7, "n"); g.px(8, 7, "n")
    # rabo balancando (aparece ao lado)
    if wag == 1:
        g.px(13, 17, d["main"]); g.px(13, 16, d["light"])
    elif wag == 2:
        g.px(2, 17, d["main"]); g.px(2, 16, d["light"])
    g.outline("r")
    return g.lines()


def back(d, wag):
    g = Grid()
    spitz = d["kind"] == "spitz"
    g.ellipse(8, 18, 5.2 if spitz else 4.6, 3.8, d["main"])
    g.rect(4, 20, 5, 22, d["main"]); g.rect(10, 20, 11, 22, d["main"])
    g.rect(4, 22, 5, 22, d["spot"]); g.rect(10, 22, 11, 22, d["spot"])
    g.ellipse(8, 13, 5.2 if spitz else 4.8, 3.9, d["main"])
    if d["kind"] == "shih":
        g.rect(2, 11, 3, 17, d["dark"]); g.rect(12, 11, 13, 17, d["dark"])
        g.rect(5, 9, 10, 10, d["light"])
    else:
        g.rect(4, 9, 5, 10, d["main"]); g.rect(10, 9, 11, 10, d["main"])
        g.px(4, 8, d["main"]); g.px(11, 8, d["main"])
    if d["bow"]:
        g.px(7, 8, d["bow"]); g.px(8, 8, d["bow"]); g.px(6, 7, d["bow"]); g.px(9, 7, d["bow"])
    # rabo curvo por cima das costas
    tx = 8 + (1 if wag == 1 else -1 if wag == 2 else 0)
    g.rect(tx - 1, 15, tx + 1, 18, d["light"])
    g.px(tx, 14, d["light"]); g.px(tx, 15, d["main"])
    g.outline("r")
    return g.lines()


def side(d, wag):
    g = Grid()
    spitz = d["kind"] == "spitz"
    # corpo horizontal
    g.ellipse(9, 18, 5.4 if spitz else 5.0, 3.4, d["main"])
    g.rect(5, 19, 6, 22, d["main"]); g.rect(11, 19, 12, 22, d["main"])
    g.rect(5, 22, 6, 22, d["spot"]); g.rect(11, 22, 12, 22, d["spot"])
    g.rect(6, 20, 11, 21, d["spot"])                                          # barriga branca
    # cabeca a esquerda
    g.ellipse(5, 14, 4.2 if spitz else 3.9, 3.7, d["main"])
    g.rect(2, 15, 4, 16, d["spot"])                                           # focinho
    g.px(2, 14, d["nose"]); g.px(3, 14, d["nose"])                            # nariz achatado
    g.px(5, 13, "r")                                                          # olho
    if d["kind"] == "shih":
        g.rect(5, 12, 7, 18, d["dark"])                                       # orelha caida
        g.rect(3, 10, 6, 11, d["light"])                                      # topete
    else:
        g.px(5, 9, d["main"]); g.px(6, 9, d["main"]); g.px(6, 10, d["main"]); g.px(5, 10, d["light"])
    if d["bow"]:
        g.px(4, 9, d["bow"]); g.px(5, 8, d["bow"]); g.px(6, 9, d["bow"]); g.px(5, 9, "n")
    # rabo enrolado para cima
    up = 1 if wag == 1 else 0
    g.rect(13, 14 - up, 14, 17, d["light"])
    g.px(14, 13 - up, d["main"]); g.px(13, 13 - up, d["light"])
    g.outline("r")
    return g.lines()


VIEWS = {"down": front, "up": back, "left": side}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, d in DOGS.items():
        for view, fn in VIEWS.items():
            frames = [fn(d, w) for w in (0, 1, 2)]
            body = "\n---\n".join("\n".join(fr) for fr in frames)
            (OUT / f"{name}_{view}.sprite.txt").write_text(
                f"# {name} (cachorro) {view}: parado e rabo balancando (16x24)\n{body}\n", encoding="utf-8")
        print("gerado:", name)


if __name__ == "__main__":
    main()
