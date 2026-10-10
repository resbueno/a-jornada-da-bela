#!/usr/bin/env python3
"""Gera os sprites das personagens (16x24) como grades de caracteres em art/src/.

Cada personagem = estilo de cabelo + cores. Direcoes: down, up, left (right = espelho no jogo).
Frames por direcao: 0 parada, 1 passo esquerdo, 2 passo direito.
Uso: python3 tools/gen_characters.py   (depois: build_sprites.py art/src assets/sprites)
"""
import sys
from pathlib import Path

W, H = 16, 24
OUT = Path(__file__).resolve().parent.parent / "art" / "src"

# letras da paleta (ver palette.json): j/k pele, r contorno, e/f madeira, t/u rosa, ...
CHARACTERS = {
    "isabela": dict(  # cabelos longos pretos, pele bronzeada, guerreira
        hair="r", hair_hi="q", skin="k", skin_sh="f", mouth="u", style="long", dress=True,
        top="t", top_sh="u", pants="e", boots="e", belt="o", accent="l", sword=True),
    "olivia": dict(   # cabelo medio castanho, pele clara
        hair="e", hair_hi="f", skin="j", skin_sh="k", style="medium", dress=True,
        top="2", top_sh="1", pants="2", boots="e", belt="f", accent="n"),       # vestido verde
    "lara": dict(     # cabelo loiro curto ate os ombros, pele clara
        hair="o", hair_hi="a", skin="j", skin_sh="k", style="short", dress=True,
        top="h", top_sh="g", pants="q", boots="e", belt="f", accent="n"),       # vestido azul
    "lana": dict(     # pele clara; cabelo ruivo curto (a definir)
        hair="p", hair_hi="o", skin="j", skin_sh="k", style="short", dress=True,
        top="l", top_sh="m", pants="b", boots="e", belt="o", accent="n"),       # vestido vermelho
    "rui": dict(      # barqueiro da ilha
        hair="q", hair_hi="h", skin="k", skin_sh="f", style="short",
        top="n", top_sh="i", pants="q", boots="e", belt="e", accent="l"),
    "sara": dict(     # pele clara, trança roxa muito longa
        hair="s", hair_hi="t", skin="j", skin_sh="k", style="braid", dress=True,
        top="o", top_sh="p", pants="q", boots="e", belt="f", accent="n"),       # vestido amarelo
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

    def outline(self, color="r"):
        """Contorno de 1 px em volta de tudo que foi pintado."""
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


def dress_legs(g, c, frame, side=False):
    """Vestido: saia em sino (4 linhas) e so os pes aparecem; a barra balanca ao andar."""
    skirt, sh = c["top"], c["top_sh"]
    rows = [(6, 10), (5, 11), (5, 11), (4, 12)] if side else [(5, 10), (4, 11), (4, 11), (3, 12)]
    for i, (x0, x1) in enumerate(rows):
        y = 17 + i
        g.rect(x0, y, x1, y, skirt)
        g.px(x1, y, sh)
        if i >= 1:
            g.px(x0 + 1, y, sh) if i == 3 and frame == 1 else None
    for x in range(rows[-1][0], rows[-1][1] + 1):       # barra com babado
        if (x + frame) % 2 == 0:
            g.px(x, 20, sh)
    left_up = 1 if frame == 1 else 0
    right_up = 1 if frame == 2 else 0
    if side:
        front = {0: 0, 1: -1, 2: 1}[frame]
        g.px(7 + front, 21, c["skin"]); g.px(7 + front, 22, c["boots"]); g.px(8 + front, 22, c["boots"])
        up = 1 if frame else 0
        g.px(8 - front, 21, c["skin"]) if not up else None
        g.px(8 - front, 22 - up, c["boots"]); g.px(9 - front, 22 - up, c["boots"])
        return
    for x0, up in ((5, left_up), (9, right_up)):
        if not up:
            g.px(x0, 21, c["skin"]); g.px(x0 + 1, 21, c["skin"])
        g.px(x0, 22 - up, c["boots"]); g.px(x0 + 1, 22 - up, c["boots"])


def legs(g, c, frame, side=False):
    """Pernas: frame 0 parado; 1 e 2 alternam a perna que sobe."""
    if c.get("dress"):
        return dress_legs(g, c, frame, side)
    left_up = 1 if frame == 1 else 0
    right_up = 1 if frame == 2 else 0
    if side:
        # de lado: uma perna a frente e outra atras
        front = {0: 0, 1: -1, 2: 1}[frame]
        g.rect(7 + front, 17, 8 + front, 21, c["pants"])
        g.rect(7 - front, 17, 8 - front, 21 - (1 if frame else 0), c["pants"])
        g.rect(7 + front, 21, 9 + front, 22, c["boots"])
        g.rect(7 - front, 21 - (1 if frame else 0), 9 - front, 22 - (1 if frame else 0), c["boots"])
        return
    g.rect(5, 17, 7, 20 - left_up, c["pants"])
    g.rect(8, 17, 10, 20 - right_up, c["pants"])
    g.rect(5, 20 - left_up, 7, 21 - left_up, c["boots"])
    g.rect(8, 20 - right_up, 10, 21 - right_up, c["boots"])


def torso(g, c, frame, view):
    g.rect(5, 11, 10, 16, c["top"])
    g.rect(10, 12, 10, 16, c["top_sh"])
    g.rect(5, 16, 10, 16, c["belt"])
    if view == "down":
        g.px(7, 11, c["accent"])
        g.px(8, 11, c["accent"])
    swing_l = 1 if frame == 1 else 0
    swing_r = 1 if frame == 2 else 0
    # bracos
    g.rect(4, 12 + swing_r, 4, 14 + swing_r, c["top"])
    g.px(4, 15 + swing_r, c["skin"])
    g.rect(11, 12 + swing_l, 11, 14 + swing_l, c["top_sh"])
    g.px(11, 15 + swing_l, c["skin_sh"])


def draw_down(c, frame):
    g = Grid()
    style = c["style"]
    # cabelo atras do corpo
    if style == "long":
        g.rect(3, 4, 12, 13, c["hair"])
        g.rect(4, 14, 11, 15, c["hair"])
    elif style == "medium":
        g.rect(3, 4, 12, 11, c["hair"])
    elif style == "short":
        g.rect(4, 3, 11, 9, c["hair"])
    elif style == "braid":
        g.rect(4, 3, 11, 9, c["hair"])
    legs(g, c, frame)
    torso(g, c, frame, "down")
    if style == "long":
        g.px(3, 8, c["hair_hi"]); g.px(12, 9, c["hair_hi"]); g.px(3, 11, c["hair_hi"])
    if style == "braid":                       # trança caindo sobre o ombro
        g.rect(11, 10, 12, 19, c["hair"])
        g.px(12, 20, c["hair_hi"])
        g.px(11, 12, c["hair_hi"])
        g.px(11, 15, c["hair_hi"])
    # cabeça
    g.rect(4, 3, 11, 10, c["skin"])
    g.px(4, 3, "."); g.px(11, 3, ".")
    # cabelo da frente
    g.rect(4, 2, 11, 4, c["hair"])
    g.px(4, 2, "."); g.px(11, 2, ".")
    g.rect(4, 5, 4, 9, c["hair"])
    g.rect(11, 5, 11, 9, c["hair"])
    g.px(5, 5, c["hair"]); g.px(6, 5, c["hair"]); g.px(9, 5, c["hair"]); g.px(10, 5, c["hair"])
    g.px(7, 5, c["hair"])
    g.px(6, 2, c["hair_hi"]); g.px(7, 2, c["hair_hi"]); g.px(5, 3, c["hair_hi"])
    # rosto
    g.px(6, 6, "r"); g.px(9, 6, "r"); g.px(6, 7, "r"); g.px(9, 7, "r")     # olhos 1x2
    m = c.get("mouth", c["skin_sh"])
    g.px(7, 9, m); g.px(8, 9, m)                                           # boca pequena
    if c.get("sword"):                         # cabo da espada por cima do ombro direito
        g.px(12, 9, "o"); g.px(12, 10, "f"); g.px(12, 8, "n")
    g.outline("r")
    return g.lines()


def draw_up(c, frame):
    g = Grid()
    style = c["style"]
    legs(g, c, frame)
    torso(g, c, frame, "up")
    # nas costas, o cabelo cobre a cabeça e cai
    g.rect(4, 2, 11, 10, c["hair"])
    g.px(4, 2, "."); g.px(11, 2, ".")
    if style == "long":
        g.rect(4, 11, 11, 16, c["hair"])
        g.rect(5, 11, 6, 15, c["hair_hi"])
    elif style == "medium":
        g.rect(4, 11, 11, 12, c["hair"])
    elif style == "braid":
        g.rect(7, 11, 8, 20, c["hair"])
        for y in (13, 16, 19):
            g.px(7, y, c["hair_hi"])
    g.px(6, 3, c["hair_hi"]); g.px(7, 3, c["hair_hi"])
    g.px(6, 4, c["hair_hi"])
    if c.get("sword"):                         # bainha cruzando as costas
        for k in range(8):
            g.px(5 + k, 11 + k // 2, "f")
        g.px(12, 14, "o")
    g.outline("r")
    return g.lines()


def draw_left(c, frame):
    g = Grid()
    style = c["style"]
    # cabelo atras (lado direito do sprite, pois olha para a esquerda)
    if style == "long":
        g.rect(8, 3, 12, 16, c["hair"])
    elif style == "medium":
        g.rect(8, 3, 12, 12, c["hair"])
    elif style == "short":
        g.rect(8, 3, 11, 9, c["hair"])
    elif style == "braid":
        g.rect(8, 3, 11, 9, c["hair"])
        g.rect(10, 10, 11, 20, c["hair"])
        for y in (12, 15, 18):
            g.px(10, y, c["hair_hi"])
    legs(g, c, frame, side=True)
    # tronco de lado, mais estreito
    g.rect(6, 11, 10, 16, c["top"])
    g.rect(9, 12, 10, 16, c["top_sh"])
    g.rect(6, 16, 10, 16, c["belt"])
    arm = {0: 0, 1: -1, 2: 1}[frame]
    g.rect(7 + arm, 12, 8 + arm, 14, c["top"])
    g.px(7 + arm, 15, c["skin"])
    # cabeça
    g.rect(4, 3, 10, 10, c["skin"])
    g.px(4, 3, "."); g.px(10, 3, ".")
    g.rect(4, 2, 10, 4, c["hair"])
    g.px(4, 2, "."); g.px(10, 2, ".")
    g.rect(8, 5, 10, 9, c["hair"])
    g.px(5, 5, c["hair"]); g.px(6, 5, c["hair"])
    g.px(6, 2, c["hair_hi"]); g.px(7, 2, c["hair_hi"]); g.px(5, 3, c["hair_hi"])
    g.px(6, 6, "r"); g.px(6, 7, "r")
    g.px(5, 9, c.get("mouth", c["skin_sh"]))
    g.outline("r")
    return g.lines()


DRAW = {"down": draw_down, "up": draw_up, "left": draw_left}


def villain(direction, frame):
    """Sombra Cinzenta: figura encapuzada cinza, olhos roxos brilhantes, capa esfarrapada."""
    g = Grid()
    bob = 1 if frame == 1 else 0
    g.rect(4, 2, 11, 9, "c")                    # capuz
    g.rect(3, 6, 12, 9, "c")
    g.rect(6, 5 + bob, 9, 8 + bob, "r")         # rosto na sombra
    g.px(6, 7 + bob, "s"); g.px(9, 7 + bob, "s")
    g.px(6, 6 + bob, "t"); g.px(9, 6 + bob, "t")
    g.rect(3, 10, 12, 21, "c")                  # capa
    g.rect(2, 14, 13, 21, "c")
    g.rect(10, 11, 12, 21, "b")                 # sombra da capa
    for x in range(2, 14):                       # barra rasgada
        g.px(x, 22 + (x % 3 == 0) , "c" if x % 2 else "b")
    g.rect(1, 12, 2, 17, "b"); g.rect(13, 12, 14, 17, "b")     # bracos
    g.px(1, 18, "d"); g.px(14, 18, "d")                          # maos palidas
    g.px(5, 3, "d"); g.px(6, 3, "d")                             # brilho do capuz
    g.outline("r")
    return g.lines()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    only = [a for a in (sys.argv[1:] or list(CHARACTERS)) if a in CHARACTERS]
    for name in only:
        c = CHARACTERS[name]
        for direction, fn in DRAW.items():
            frames = [fn(c, f) for f in range(3)]
            body = "\n---\n".join("\n".join(fr) for fr in frames)
            (OUT / f"{name}_{direction}.sprite.txt").write_text(
                f"# {name} olhando para {direction}: parada, passo 1, passo 2 (16x24)\n{body}\n",
                encoding="utf-8",
            )
        print("gerado:", name)
    if not sys.argv[1:] or "sombra" in sys.argv[1:]:
        frames = [villain("down", f) for f in range(3)]
        body = "\n---\n".join("\n".join(fr) for fr in frames)
        for d in ("down", "up", "left"):
            (OUT / f"sombra_{d}.sprite.txt").write_text(
                f"# Sombra Cinzenta (vilao) {d}: 3 frames 16x24\n{body}\n", encoding="utf-8")
        print("gerado: sombra")


if __name__ == "__main__":
    main()
