#!/usr/bin/env python3
"""Gera os sprites das personagens em alta resolucao (32x48) em art/src/.

Cada personagem e desenhada na grade base 16x24 (estilo de cabelo + cores + pecas de roupa) e
depois passa pelo pipeline `pixel.hd` (2x com EPX, contorno fino, sombra e brilho) e por um
acabamento do rosto (olhos com brilho, bochechas e sorriso).
Direcoes: down, up, left (right = espelho no jogo). Quadros: 0 parada, 1 e 2 passos.
Uso: python3 tools/gen_characters.py [nome ...]   (depois: tools/build_sprites.py)
"""
import sys

import pixel

W, H = 16, 24

# letras da paleta: j/k pele, r contorno/preto, e/f madeira, t/u rosa, o/p amarelo/laranja ...
BASE = {
    "isabela": dict(  # cabelos longos pretos, pele bronzeada, Lanterna do Coracao
        hair="r", hair_hi="q", skin="k", skin_sh="f", style="long", dress=True,
        top="t", top_sh="u", pants="e", boots="e", belt="o", accent="n", lantern=True),
    "olivia": dict(   # cabelo medio castanho, pele clara
        hair="e", hair_hi="f", skin="j", skin_sh="k", style="medium", dress=True,
        top="2", top_sh="1", pants="2", boots="e", belt="f", accent="n"),
    "lara": dict(     # cabelo loiro curto ate os ombros, pele clara
        hair="o", hair_hi="a", skin="j", skin_sh="k", style="short", dress=True,
        top="h", top_sh="g", pants="q", boots="e", belt="f", accent="n"),
    "lana": dict(     # pele clara, cabelo preto em maria-chiquinha
        hair="r", hair_hi="q", ties="l", skin="j", skin_sh="k", style="pigtails", dress=True,
        top="l", top_sh="m", pants="b", boots="e", belt="o", accent="n"),
    "evelyn": dict(   # japonesa, pele branca, cabelo preto longo com franja reta, segura a encomenda
        hair="r", hair_hi="q", skin="j", skin_sh="k", style="long", dress=True, bangs=True, parcel=True,
        top="i", top_sh="h", pants="e", boots="n", belt="h", accent="l"),
    "william": dict(  # pele como a da Isabela, cabelo preto com coque samurai, jaleco de medico
        hair="r", hair_hi="q", skin="k", skin_sh="f", style="short", topknot=True, coat=True,
        top="h", top_sh="g", pants="q", boots="e", belt="q", accent="n"),
    "rui": dict(      # barqueiro do vale
        hair="q", hair_hi="h", skin="k", skin_sh="f", style="short",
        top="n", top_sh="i", pants="q", boots="e", belt="e", accent="l"),
}

# Roupas por fase (ver STORY_V2.md): mesmo cabelo e rosto, outra roupa
OUTFITS = {
    "isabela_bosque": ("isabela", dict(     # capa verde-musgo, tunica creme, calca e botas de couro
        dress=False, top="2", top_sh="1", pants="f", boots="e", belt="e", accent="a", cape=True)),
    "isabela_chuva": ("isabela", dict(      # capa de chuva amarela com capuz e galochas vermelhas
        top="o", top_sh="p", belt="o", accent="n", boots="l", hood=True, galoshes=True)),
    "isabela_vento": ("isabela", dict(      # casaco roxo, cachecol vermelho e gorro com pompom
        dress=False, top="s", top_sh="q", pants="q", boots="e", belt="s", accent="l", scarf=True, beanie=True)),
    "isabela_gala": ("isabela", dict(       # vestido rosa do banquete, faixa dourada, tiara e pingente
        tiara=True, lantern=False, pendant=True)),
    "lana_bosque": ("lana", dict(           # colete de aventureira, camiseta laranja, bermuda e corda
        dress=False, top="p", top_sh="m", pants="f", boots="e", belt="e", accent="p", vest="e",
        rope=True, shorts=True)),
    "lana_chuva": ("lana", dict(            # capa de chuva azul-marinho, galochas amarelas, colete salva-vidas
        top="q", top_sh="r", belt="q", accent="n", boots="o", galoshes="o", lifevest=True)),
    "lana_vento": ("lana", dict(            # jaqueta corta-vento verde, calca de escalada e mochila
        dress=False, top="2", top_sh="1", pants="e", boots="e", belt="1", accent="3", backpack=True)),
    "lana_gala": ("lana", dict(             # vestido laranja e uma pena numa das maria-chiquinhas
        top="p", top_sh="m", belt="o", accent="n", feather=True)),
    "lara_chuva": ("lara", dict(            # jardineira jeans, colete salva-vidas, galochas e chapeu de pescador
        dress=False, top="h", top_sh="g", pants="h", boots="2", belt="g", accent="n", straps=True,
        lifevest=True, galoshes="2", bucket_hat=True)),
    "lara_vento": ("lara", dict(            # macacao listrado de maquinista, oculos na testa e cinto de ferramentas
        dress=False, top="q", top_sh="r", pants="q", boots="e", belt="f", accent="n", stripes=True,
        goggles=True, tools=True)),
    "lara_gala": ("lara", dict(             # vestido amarelo
        top="o", top_sh="p", belt="f", accent="n")),
    "olivia_vento": ("olivia", dict(        # bone de maquinista listrado, lenco vermelho, jaqueta de la, flauta
        dress=False, top="a", top_sh="9", pants="q", boots="e", belt="f", accent="l", cap=True,
        scarf=True, flute=True)),
    "olivia_gala": ("olivia", dict(         # vestido azul-claro com capinha
        top="i", top_sh="h", belt="v", accent="n", cape_color=("v", "h"), cape=True)),
}


def character(name):
    if name in BASE:
        return BASE[name]
    base, extra = OUTFITS[name]
    return dict(BASE[base], **extra)


ALL = list(BASE) + list(OUTFITS)


class Grid(pixel.Grid):
    def __init__(self):
        super().__init__(W, H)

    def outline(self, color=pixel.OUTLINE):
        super().outline(color)


# ----------------------------------------------------------------------------- corpo
def dress_legs(g, c, frame, side=False):
    """Vestido: saia em sino (4 linhas) e so os pes aparecem; a barra balanca ao andar."""
    skirt, sh = c["top"], c["top_sh"]
    rows = [(6, 10), (5, 11), (5, 11), (4, 12)] if side else [(5, 10), (4, 11), (4, 11), (3, 12)]
    for i, (x0, x1) in enumerate(rows):
        y = 17 + i
        g.rect(x0, y, x1, y, skirt)
        g.px(x1, y, sh)
    for x in range(rows[-1][0], rows[-1][1] + 1):       # barra com babado
        if (x + frame) % 2 == 0:
            g.px(x, 20, sh)
    feet(g, c, frame, side)


def feet(g, c, frame, side):
    if side:
        front = {0: 0, 1: -1, 2: 1}[frame]
        up = 1 if frame else 0
        g.px(7 + front, 21, c["skin"]); g.px(7 + front, 22, c["boots"]); g.px(8 + front, 22, c["boots"])
        if not up:
            g.px(8 - front, 21, c["skin"])
        g.px(8 - front, 22 - up, c["boots"]); g.px(9 - front, 22 - up, c["boots"])
        return
    for x0, up in ((5, 1 if frame == 1 else 0), (9, 1 if frame == 2 else 0)):
        if not up:
            g.px(x0, 21, c["skin"]); g.px(x0 + 1, 21, c["skin"])
        g.px(x0, 22 - up, c["boots"]); g.px(x0 + 1, 22 - up, c["boots"])


def legs(g, c, frame, side=False):
    """Pernas: frame 0 parado; 1 e 2 alternam a perna que sobe."""
    if c.get("dress"):
        return dress_legs(g, c, frame, side)
    pants = c["pants"]
    knee = 18 if c.get("shorts") else 99            # bermuda: joelho e canela de fora
    if side:
        front = {0: 0, 1: -1, 2: 1}[frame]
        lift = 1 if frame else 0
        g.rect(7 + front, 17, 8 + front, 21, pants)
        g.rect(7 - front, 17, 8 - front, 21 - lift, pants)
        if knee < 99:
            g.rect(7 + front, knee + 1, 8 + front, 20, c["skin"])
            g.rect(7 - front, knee + 1, 8 - front, 20 - lift, c["skin"])
        g.rect(7 + front, 21, 9 + front, 22, c["boots"])
        g.rect(7 - front, 21 - lift, 9 - front, 22 - lift, c["boots"])
        return
    lu = 1 if frame == 1 else 0
    ru = 1 if frame == 2 else 0
    g.rect(5, 17, 7, 20 - lu, pants)
    g.rect(8, 17, 10, 20 - ru, pants)
    if knee < 99:
        g.rect(5, knee + 1, 7, 19 - lu, c["skin"])
        g.rect(8, knee + 1, 10, 19 - ru, c["skin"])
    g.rect(5, 20 - lu, 7, 21 - lu, c["boots"])
    g.rect(8, 20 - ru, 10, 21 - ru, c["boots"])


def torso(g, c, frame, view):
    g.rect(5, 11, 10, 16, c["top"])
    g.rect(10, 12, 10, 16, c["top_sh"])
    g.rect(5, 16, 10, 16, c["belt"])
    if view == "down":
        g.px(7, 11, c["accent"]); g.px(8, 11, c["accent"])
    swing_l = 1 if frame == 1 else 0
    swing_r = 1 if frame == 2 else 0
    g.rect(4, 12 + swing_r, 4, 14 + swing_r, c["top"])
    g.px(4, 15 + swing_r, c["skin"])
    g.rect(11, 12 + swing_l, 11, 14 + swing_l, c["top_sh"])
    g.px(11, 15 + swing_l, c["skin_sh"])


def coat(g, c, view, frame):
    """Jaleco branco ate o joelho, aberto na frente, com estetoscopio e bolso."""
    if view == "left":
        g.rect(6, 11, 10, 18, "n"); g.rect(9, 12, 10, 18, "d"); g.rect(6, 18, 10, 18, "d"); g.px(7, 14, "d")
        return
    g.rect(5, 11, 10, 18, "n"); g.rect(10, 12, 10, 18, "d")
    g.rect(4, 11, 4, 15, "n"); g.rect(11, 11, 11, 15, "d")
    g.px(4, 16, c["skin"]); g.px(11, 16, c["skin_sh"])
    if view == "down":
        g.rect(7, 11, 8, 17, c["top"])
        g.rect(6, 12, 6, 17, "d"); g.rect(9, 12, 9, 17, "d")
        g.px(5, 15, "d"); g.px(6, 15, "d")
        g.px(6, 11, "r"); g.px(9, 11, "r"); g.px(6, 12, "r"); g.px(9, 12, "r"); g.px(9, 13, "r"); g.px(9, 14, "c")
    else:
        g.rect(7, 12, 7, 18, "d")


def parcel(g, side=False):
    """Caixa laranja de encomenda (fita branca) carregada na frente do corpo."""
    x0, x1 = (3, 7) if side else (4, 11)
    g.rect(x0, 12, x1, 16, "p"); g.rect(x0, 12, x1, 12, "o")
    cx = (x0 + x1) // 2
    g.rect(cx, 12, cx + (0 if side else 1), 16, "n")
    g.px(x0, 15, "j"); g.px(x1, 15, "j")


def topknot_head(g, c, view):
    """Cabeca do Tio William: laterais curtas, testa livre e coque samurai no alto."""
    h, hi, sk, sh = c["hair"], c["hair_hi"], c["skin"], c["skin_sh"]
    g.rect(2, 0, 13, 10, ".")
    g.rect(6, 0, 9, 1, h); g.px(7, 0, hi); g.px(6, 1, hi)
    g.rect(6, 2, 9, 2, "l")
    g.rect(5, 3, 10, 3, h)
    if view == "left":
        g.rect(4, 4, 10, 10, sk); g.px(4, 4, ".")
        g.rect(5, 3, 9, 3, h); g.rect(5, 4, 10, 4, h); g.rect(8, 5, 10, 8, h)
        g.px(7, 6, sh); g.px(7, 7, sh); g.rect(8, 9, 10, 10, sh)
        g.px(6, 6, "r"); g.px(6, 7, "r"); g.px(5, 9, sh)
        return
    g.rect(4, 4, 11, 10, sk); g.rect(5, 3, 10, 3, h)
    if view == "up":
        g.rect(4, 4, 11, 8, h); g.rect(5, 9, 10, 10, sh); g.px(5, 5, hi); g.px(6, 5, hi)
        return
    g.px(4, 4, h); g.px(11, 4, h); g.rect(4, 5, 4, 6, h); g.rect(11, 5, 11, 6, h); g.px(5, 3, hi)
    g.rect(5, 5, 6, 5, "f"); g.rect(9, 5, 10, 5, "f")
    g.rect(6, 6, 6, 7, "r"); g.rect(9, 6, 9, 7, "r")
    g.px(7, 9, sh); g.px(8, 9, sh)


def pigtails(g, c, view):
    """Maria-chiquinha: dois rabinhos presos com elastico, um de cada lado da cabeca."""
    h, hi, tie = c["hair"], c["hair_hi"], c.get("ties", c["hair_hi"])
    sides = [(10, 12)] if view == "left" else [(2, 3), (12, 13)]
    for x0, x1 in sides:
        g.rect(x0, 5, x1, 5, tie)
        g.rect(x0, 6, x1, 10, h)
        g.px(x0 if x0 < 8 else x1, 11, h)
        g.px(x0, 7, hi)
    if c.get("feather"):                                  # pena branca presa no elastico
        x = sides[-1][1]
        g.px(x, 3, "n"); g.px(x + 1, 2, "n"); g.px(x, 4, "i")


# ----------------------------------------------------------------------------- pecas de roupa
def hood(g, view):
    """Capuz amarelo da capa de chuva por cima do cabelo (o rosto fica livre)."""
    if view == "up":
        g.rect(3, 1, 12, 10, "o"); g.rect(4, 11, 11, 17, "o")
        g.rect(11, 2, 12, 17, "p"); g.px(5, 2, "a"); g.px(6, 2, "a"); g.rect(7, 11, 8, 16, "p")
        return
    if view == "left":
        g.rect(3, 1, 10, 4, "o"); g.rect(8, 1, 12, 11, "o"); g.rect(11, 3, 12, 11, "p")
        g.px(3, 1, "."); g.px(5, 1, "a"); g.px(3, 5, "o")
        return
    g.rect(3, 1, 12, 4, "o"); g.px(3, 1, "."); g.px(12, 1, ".")
    g.rect(3, 5, 3, 10, "o"); g.rect(12, 5, 12, 10, "p")
    g.px(5, 1, "a"); g.px(6, 1, "a")
    g.px(7, 13, "n"); g.px(7, 15, "n")                                  # botoes grandes


def galoshes(g, c):
    """Galochas: o cano sobe e cobre o tornozelo."""
    color = c["galoshes"] if isinstance(c["galoshes"], str) else "l"
    for y in (21, 22):
        for x in range(W):
            if g.g[y][x] in (c["skin"], c["skin_sh"], c["boots"]):
                g.px(x, y, color)


def cape(g, c, view):
    """Capa nas costas (de frente, so as bordas nos ombros)."""
    main, sh = c.get("cape_color", ("2", "1"))
    if view == "up":
        g.rect(3, 11, 12, 19, main); g.rect(10, 11, 12, 19, sh)
        for x in range(3, 13, 2):
            g.px(x, 19, sh)
        return
    if view == "left":
        g.rect(10, 11, 12, 18, main); g.rect(12, 12, 12, 18, sh)
        return
    g.rect(3, 11, 3, 17, main); g.rect(12, 11, 12, 17, sh)
    if not c.get("dress"):
        g.rect(6, 12, 9, 15, "a")                                       # tunica creme por baixo


def lantern(g, side=False):
    """Lanterna do Coracao presa no cinto: coracao rosa que brilha."""
    x = 6 if side else 9
    g.px(x, 16, "o"); g.px(x, 17, "t"); g.px(x + (0 if side else 1), 17, "u"); g.px(x, 18, "o")


def pendant(g, view):
    """No vestido de gala, a lanterna vira um pingente de coracao no peito."""
    if view == "down":
        g.px(7, 12, "o"); g.px(8, 12, "o"); g.px(7, 13, "t"); g.px(8, 13, "u")


def scarf(g, view, frame):
    """Cachecol vermelho no pescoco, com a ponta voando no vento."""
    wave = frame % 2
    if view == "left":
        g.rect(5, 11, 10, 11, "l")
        g.rect(11, 11 + wave, 13, 11 + wave, "l"); g.px(13, 12 - wave, "m")
        return
    g.rect(5, 11, 10, 11, "l"); g.rect(5, 11, 5, 12, "m")
    if view == "down":
        g.rect(9, 12, 9, 14, "l"); g.px(9, 14, "m")
    else:
        g.rect(12, 11 + wave, 13, 11 + wave, "l"); g.px(13, 12 - wave, "m")


def beanie(g, view):
    """Gorro de la vermelho com barra branca e pompom."""
    x1 = 10 if view == "left" else 11
    g.rect(4, 1, x1, 3, "l"); g.rect(4, 4, x1, 4, "n")
    g.px(4, 1, "."); g.px(x1, 1, ".")
    g.px(5, 2, "t"); g.rect(7, 0, 8, 0, "n")


def cap(g, view):
    """Bone de maquinista listrado de azul e branco, com aba."""
    x1 = 10 if view == "left" else 11
    for x in range(4, x1 + 1):
        g.rect(x, 1, x, 3, "q" if x % 2 else "n")
    g.px(4, 1, "."); g.px(x1, 1, ".")
    if view == "left":
        g.rect(2, 4, 6, 4, "q")                                         # aba para a frente
    elif view == "down":
        g.rect(4, 4, 11, 4, "q")
    else:
        g.rect(4, 4, 11, 4, "n")


def bucket_hat(g, view):
    """Chapeu de pescador amarelo, aba larga."""
    x1 = 10 if view == "left" else 11
    g.rect(5, 0, x1 - 1, 2, "o"); g.rect(3, 3, x1 + 1, 3, "o"); g.rect(3, 4, x1 + 1, 4, "p")
    g.px(6, 1, "a")


def tiara(g, view):
    """Tiara dourada com uma pedra no centro."""
    if view == "up":
        g.rect(5, 2, 10, 2, "o")
        return
    x1 = 8 if view == "left" else 9
    g.rect(5, 2, x1, 2, "o"); g.px(7 if view == "down" else 6, 1, "o")
    g.px(7 if view == "down" else 6, 2, "t")


def goggles(g, view):
    """Oculos de protecao na testa."""
    if view == "up":
        g.rect(4, 5, 11, 5, "b")
        return
    if view == "left":
        g.rect(4, 4, 7, 4, "b"); g.px(4, 4, "i"); g.px(5, 4, "v")
        return
    g.rect(4, 4, 11, 4, "b"); g.rect(5, 4, 6, 4, "v"); g.rect(9, 4, 10, 4, "v"); g.px(5, 4, "i"); g.px(9, 4, "i")


def vest(g, c, view):
    color = c["vest"]
    if view == "left":
        g.rect(8, 11, 10, 15, color)
        return
    if view == "up":
        g.rect(5, 11, 10, 15, color)
        return
    g.rect(5, 11, 6, 15, color); g.rect(9, 11, 10, 15, color)
    g.px(5, 13, "f"); g.px(10, 13, "f")                                 # bolsinhos


def rope(g, view):
    """Corda enrolada a tiracolo."""
    if view == "left":
        g.rect(9, 12, 11, 14, "9"); g.px(10, 13, "a")
        return
    for k in range(6):
        g.px(5 + k, 11 + k, "a" if k % 2 else "9")


def lifevest(g, view):
    """Colete salva-vidas laranja com faixas brancas."""
    if view == "left":
        g.rect(6, 11, 10, 15, "p"); g.rect(6, 13, 10, 13, "n")
        return
    g.rect(5, 11, 10, 15, "p")
    g.rect(5, 13, 10, 13, "n")
    if view == "down":
        g.rect(7, 11, 8, 15, "o")                                       # ziper


def straps(g, view):
    """Alcas da jardineira sobre a camiseta branca."""
    if view == "down":
        g.rect(5, 11, 10, 12, "n"); g.px(6, 11, "h"); g.px(9, 11, "h"); g.px(6, 12, "h"); g.px(9, 12, "h")
        g.px(6, 13, "o"); g.px(9, 13, "o")


def stripes(g, view):
    """Listras verticais do macacao de maquinista."""
    x0, x1 = (6, 10) if view == "left" else (5, 10)
    for x in range(x0, x1 + 1, 2):
        for y in range(11, 21):
            if g.g[y][x] in ("q", "r"):
                g.px(x, y, "n")


def tools(g, view):
    """Cinto de ferramentas: chave inglesa e martelinho."""
    if view == "up":
        return
    x = 5 if view == "down" else 6
    g.rect(x, 16, x + 5 if view == "down" else x + 4, 16, "f")
    g.px(x, 17, "d"); g.px(x, 18, "d"); g.px(x + 4, 17, "c")


def backpack(g, view):
    if view == "up":
        g.rect(5, 12, 10, 17, "f"); g.rect(5, 12, 10, 12, "e"); g.px(7, 14, "e"); g.px(8, 14, "e")
        g.px(6, 11, "e"); g.px(9, 11, "e")
    elif view == "left":
        g.rect(10, 12, 12, 17, "f"); g.rect(12, 13, 12, 17, "e")
    else:
        g.px(5, 11, "e"); g.px(10, 11, "e"); g.px(5, 12, "e"); g.px(10, 12, "e")


def flute(g, view):
    """Flauta presa no cinto."""
    if view == "down":
        g.rect(4, 16, 4, 19, "n"); g.px(4, 17, "d")
    elif view == "left":
        g.rect(6, 16, 6, 19, "n")


def outfit(g, c, view, frame):
    """Pecas de roupa por cima do corpo base (desenhadas antes do contorno)."""
    side = view == "left"
    if c.get("vest"):
        vest(g, c, view)
    if c.get("lifevest"):
        lifevest(g, view)
    if c.get("straps"):
        straps(g, view)
    if c.get("stripes"):
        stripes(g, view)
    if c.get("rope"):
        rope(g, view)
    if c.get("cape") and view != "up":
        cape(g, c, view)
    if c.get("backpack"):
        backpack(g, view)
    if c.get("lantern") and view != "up":
        lantern(g, side)
    if c.get("pendant"):
        pendant(g, view)
    if c.get("tools"):
        tools(g, view)
    if c.get("flute"):
        flute(g, view)
    if c.get("galoshes"):
        galoshes(g, c)
    if c.get("scarf"):
        scarf(g, view, frame)
    if c.get("hood"):
        hood(g, view)
    if c.get("beanie"):
        beanie(g, view)
    if c.get("cap"):
        cap(g, view)
    if c.get("bucket_hat"):
        bucket_hat(g, view)
    if c.get("goggles"):
        goggles(g, view)
    if c.get("tiara"):
        tiara(g, view)


# ----------------------------------------------------------------------------- vistas
def draw_down(c, frame):
    g = Grid()
    style = c["style"]
    if style == "long":
        g.rect(3, 4, 12, 13, c["hair"]); g.rect(4, 14, 11, 15, c["hair"])
    elif style == "medium":
        g.rect(3, 4, 12, 11, c["hair"])
    elif style in ("short", "pigtails"):
        g.rect(4, 3, 11, 9, c["hair"])
    if style == "pigtails":
        pigtails(g, c, "down")
    legs(g, c, frame)
    torso(g, c, frame, "down")
    if c.get("coat"):
        coat(g, c, "down", frame)
    if style == "long":
        g.px(3, 8, c["hair_hi"]); g.px(12, 9, c["hair_hi"]); g.px(3, 11, c["hair_hi"])
    g.rect(4, 3, 11, 10, c["skin"])                                        # cabeca
    g.px(4, 3, "."); g.px(11, 3, ".")
    g.rect(4, 2, 11, 4, c["hair"])                                         # cabelo da frente
    g.px(4, 2, "."); g.px(11, 2, ".")
    g.rect(4, 5, 4, 9, c["hair"]); g.rect(11, 5, 11, 9, c["hair"])
    for x in (5, 6, 7, 9, 10):
        g.px(x, 5, c["hair"])
    if c.get("bangs"):
        g.rect(4, 5, 11, 5, c["hair"])
    g.px(6, 2, c["hair_hi"]); g.px(7, 2, c["hair_hi"]); g.px(5, 3, c["hair_hi"])
    g.px(6, 6, "r"); g.px(9, 6, "r"); g.px(6, 7, "r"); g.px(9, 7, "r")     # olhos (refeitos no hd)
    if c.get("parcel"):
        parcel(g)
    if c.get("topknot"):
        topknot_head(g, c, "down")
    outfit(g, c, "down", frame)
    g.outline()
    return g


def draw_up(c, frame):
    g = Grid()
    style = c["style"]
    legs(g, c, frame)
    torso(g, c, frame, "up")
    if c.get("coat"):
        coat(g, c, "up", frame)
    if c.get("cape"):
        cape(g, c, "up")
    if c.get("backpack") and style != "long":
        backpack(g, "up")
    g.rect(4, 2, 11, 10, c["hair"])
    g.px(4, 2, "."); g.px(11, 2, ".")
    if style == "long":
        g.rect(4, 11, 11, 16, c["hair"]); g.rect(5, 11, 6, 15, c["hair_hi"])
    elif style == "medium":
        g.rect(4, 11, 11, 12, c["hair"])
    elif style == "pigtails":
        pigtails(g, c, "up")
    g.px(6, 3, c["hair_hi"]); g.px(7, 3, c["hair_hi"]); g.px(6, 4, c["hair_hi"])
    if c.get("topknot"):
        topknot_head(g, c, "up")
    outfit(g, dict(c, backpack=False), "up", frame)
    g.outline()
    return g


def draw_left(c, frame):
    g = Grid()
    style = c["style"]
    if style == "long":
        g.rect(8, 3, 12, 16, c["hair"])
    elif style == "medium":
        g.rect(8, 3, 12, 12, c["hair"])
    elif style in ("short", "pigtails"):
        g.rect(8, 3, 11, 9, c["hair"])
    if style == "pigtails":
        pigtails(g, c, "left")
    legs(g, c, frame, side=True)
    g.rect(6, 11, 10, 16, c["top"])                                        # tronco de lado
    g.rect(9, 12, 10, 16, c["top_sh"])
    g.rect(6, 16, 10, 16, c["belt"])
    if c.get("coat"):
        coat(g, c, "left", frame)
    arm = {0: 0, 1: -1, 2: 1}[frame]
    g.rect(7 + arm, 12, 8 + arm, 14, "n" if c.get("coat") else c["top"])
    g.px(7 + arm, 15, c["skin"])
    g.rect(4, 3, 10, 10, c["skin"])                                        # cabeca
    g.px(4, 3, "."); g.px(10, 3, ".")
    g.rect(4, 2, 10, 4, c["hair"])
    g.px(4, 2, "."); g.px(10, 2, ".")
    g.rect(8, 5, 10, 9, c["hair"])
    g.px(5, 5, c["hair"]); g.px(6, 5, c["hair"])
    g.px(6, 2, c["hair_hi"]); g.px(7, 2, c["hair_hi"]); g.px(5, 3, c["hair_hi"])
    g.px(6, 6, "r"); g.px(6, 7, "r")
    if c.get("topknot"):
        topknot_head(g, c, "left")
    if c.get("bangs"):
        g.rect(4, 5, 7, 5, c["hair"])
    if c.get("parcel"):
        parcel(g, side=True)
    outfit(g, c, "left", frame)
    g.outline()
    return g


DRAW = {"down": draw_down, "up": draw_up, "left": draw_left}


# ----------------------------------------------------------------------------- acabamento hd
def face(big, c, view):
    """Olhos com brilho e cilios, bochechas rosadas e um sorriso (na grade 32x48)."""
    skin, sh = c["skin"], c["skin_sh"]
    blush = "t" if skin == "j" else "u"
    eyes = [12, 18] if view == "down" else ([11] if view == "left" else [])
    for ex in eyes:
        big.rect(ex, 12, ex + 1, 15, skin)
        big.rect(ex, 13, ex + 1, 15, "r")                    # olho
        big.px(ex, 13, "n")                                  # brilho
        big.px(ex + 1, 15, "e")                              # iris castanha
        big.px(ex - 1 if ex < 16 else ex + 2, 12, "r")       # cilio
    if view == "down":
        big.rect(14, 18, 17, 19, skin)
        big.px(14, 18, sh); big.px(17, 18, sh); big.rect(15, 19, 16, 19, "u")   # sorriso
        big.rect(10, 17, 11, 17, blush); big.rect(20, 17, 21, 17, blush)
    elif view == "left":
        big.rect(9, 18, 11, 19, skin)
        big.px(9, 18, sh); big.px(10, 19, "u")
        big.rect(13, 17, 14, 17, blush)


def make(name, view, frame):
    c = character(name)
    base = DRAW[view](c, frame)
    big = pixel.hd(base, skip=(c["skin"],))
    if not c.get("topknot"):
        face(big, c, view)
    return big


def main():
    names = [a for a in (sys.argv[1:] or ALL) if a in BASE or a in OUTFITS]
    for name in names:
        for view in DRAW:
            pixel.save(f"{name}_{view}", [make(name, view, f) for f in range(3)],
                       f"{name} olhando para {view}: parada, passo 1, passo 2 (32x48)")
        print("gerado:", name)


if __name__ == "__main__":
    main()
