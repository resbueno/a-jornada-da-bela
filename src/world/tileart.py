"""Arte do terreno gerada por codigo, na paleta de 32 cores.

Cada tile 16x16 e montado de forma deterministica (mesmo mapa = mesma imagem).
O mapa inteiro e pre-renderizado em 2 quadros (agua animada) e a camera so
recorta a regiao visivel.
"""
import random

import pygame

from src import config
from src.world.terrain import Terrain

T = config.TILE
P = config.PALETTE

LAND_PATH = {Terrain.DIRT}


def _h(tx, ty, salt=0):
    return ((tx * 73856093) ^ (ty * 19349663) ^ (salt * 83492791)) & 0x7FFFFFFF


def _surface():
    return pygame.Surface((T, T), pygame.SRCALPHA)


def _put(s, x, y, color):
    s.set_at((x % T, y % T), P[color])


def _line(s, x0, y0, x1, y1, color):
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        _put(s, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


# --------------------------------------------------------------- chao
def _ground_variant(i):
    rng = random.Random(1000 + i)
    s = _surface()
    s.fill(P["chao"])
    for _ in range(3):  # tufos
        x, y = rng.randrange(1, T - 3), rng.randrange(2, T - 1)
        _put(s, x, y, "chao_sombra")
        _put(s, x + 2, y, "chao_sombra")
        _put(s, x + 1, y - 1, "chao_claro")
    for _ in range(4):  # pontinhos claros
        _put(s, rng.randrange(T), rng.randrange(T), "chao_claro")
    return s


def _flower(color_a, color_b):
    s = _surface()
    _put(s, 1, 0, color_a)
    _put(s, 0, 1, color_a)
    _put(s, 2, 1, color_a)
    _put(s, 1, 2, color_a)
    _put(s, 1, 1, color_b)
    return s


# --------------------------------------------------------------- trilha
def _path_base(i):
    rng = random.Random(2000 + i)
    s = _surface()
    s.fill(P["areia"])
    for _ in range(7):
        _put(s, rng.randrange(T), rng.randrange(T), "areia_sombra")
    for _ in range(5):
        _put(s, rng.randrange(T), rng.randrange(T), "areia_clara")
    return s


# --------------------------------------------------------------- grama alta
def _tall_grass_variant(i):
    s = _surface()
    base = [(0, 0), (8, 0), (4, 8), (12, 8)] if i == 0 else [(0, 4), (8, 4), (4, 12), (12, 12)]
    for ox, oy in base:
        bx, by = ox + 4, oy + 7
        for ex, ey in ((0, 3), (1, 1), (4, 0), (6, 1), (7, 3)):
            tx, ty = ox + ex, oy + ey
            _line(s, bx, by, tx, ty, "verde_escuro")
            mx, my = (bx + tx) // 2, (by + ty) // 2
            _put(s, mx, my, "verde_medio")
            _put(s, tx, ty, "verde_claro")
        _put(s, bx, by, "verde_contorno")
        _put(s, bx - 1, by, "verde_contorno")
        _put(s, bx + 1, by, "verde_contorno")
    return s


# --------------------------------------------------------------- pinheiro grande (2x2 tiles)
def _big_pine(i):
    """Pinheiro 32x32 em 3 camadas, com tronco e sombra no chao; vira 4 quadrantes de 16x16."""
    rng = random.Random(5000 + i)
    s = pygame.Surface((2 * T, 2 * T), pygame.SRCALPHA)

    def put(x, y, c):
        if 0 <= x < 2 * T and 0 <= y < 2 * T:
            s.set_at((x, y), P[c])

    for x in range(7, 25):                       # sombra no chao
        for y in (30, 31):
            if (x - 15.5) ** 2 / 81 + (y - 31) ** 2 / 2 <= 1:
                put(x, y, "chao_sombra")
    for y in range(28, 32):                      # tronco
        put(14, y, "madeira_escura"); put(15, y, "madeira")
        put(16, y, "madeira"); put(17, y, "madeira_escura")
    tiers = [(1, 12, 6, 18), (9, 12, 12, 26), (17, 12, 20, 32)]
    for start, rows, w0, w1 in tiers:
        for r in range(rows):
            w = w0 + (w1 - w0) * r // (rows - 1)
            w -= w % 2
            x0 = (2 * T - w) // 2
            last = r == rows - 1
            for x in range(w):
                y = start + r
                if x == 0 or x == w - 1:
                    color = "verde_contorno"
                elif last:
                    color = "verde_contorno" if x % 2 == 0 else "verde_escuro"
                else:
                    u = (x - (w - 1) / 2) / max((w - 1) / 2, 1)
                    if u < -0.5:
                        color = "verde_claro"
                    elif u < 0.1:
                        color = "verde_medio"
                    else:
                        color = "verde_escuro"
                    if u < -0.7 and r < rows - 3 and rng.random() < 0.55:
                        color = "verde_brilho"
                    elif r % 4 == 2 and rng.random() < 0.25:
                        color = "verde_escuro" if color != "verde_escuro" else "verde_medio"
                put(x0 + x, y, color)
    return [[s.subsurface((qx * T, qy * T, T, T)).copy() for qx in range(2)] for qy in range(2)]


def _rock():
    s = _surface()
    for x in range(3, 14):                       # sombra
        _put(s, x, 14, "chao_sombra")
    for y in range(3, 14):
        for x in range(2, 14):
            dx, dy = (x - 7.5) / 6.0, (y - 8.5) / 5.2
            if dx * dx + dy * dy <= 1.0:
                edge = (dx * dx + dy * dy) > 0.72
                if edge:
                    c = "rocha_contorno"
                elif dx + dy < -0.35:
                    c = "rocha_clara"
                elif dx + dy > 0.35:
                    c = "rocha"
                else:
                    c = "rocha"
                _put(s, x, y, c)
    _put(s, 5, 5, "branco"); _put(s, 6, 5, "rocha_clara")
    return s


# --------------------------------------------------------------- pedra / castelo
def _stone_floor(i):
    rng = random.Random(4000 + i)
    s = _surface()
    s.fill(P["rocha"])
    for _ in range(8):
        _put(s, rng.randrange(T), rng.randrange(T), "rocha_contorno")
    for _ in range(6):
        _put(s, rng.randrange(T), rng.randrange(T), "rocha_clara")
    return s


def _castle(top, bottom, door):
    s = _surface()
    s.fill(P["rocha_clara"])
    for y in range(T):                       # tijolos
        if y % 4 == 3:
            for x in range(T):
                _put(s, x, y, "rocha")
        else:
            off = 4 if (y // 4) % 2 else 0
            for x in range(off, T, 8):
                _put(s, x, y, "rocha")
    if top:                                  # ameias
        for x in range(T):
            for y in range(0, 4):
                if (x // 4) % 2 == 1:
                    _put(s, x, y, "chao_claro" if False else "rocha_clara")
                else:
                    _put(s, x, y, "ceu" if y < 3 else "rocha_contorno")
        for x in range(T):
            _put(s, x, 4, "rocha_contorno")
    if door:
        for y in range(5, T):
            for x in range(4, 12):
                edge = x in (4, 11) or y == 5
                _put(s, x, y, "rocha_contorno" if edge else "madeira_escura")
        for y in range(6, T):
            _put(s, 7, y, "madeira")
        _put(s, 9, 11, "amarelo")
    if bottom:
        for x in range(T):
            _put(s, x, T - 1, "rocha_contorno")
    return s


def _fissure(tx, ty, n_same, s_same):
    """Fenda escura com bordas irregulares e brilho ao fundo."""
    rng = random.Random(_h(tx, ty, 21))
    s = _surface()
    s.fill(P["rocha_contorno"])
    for y in range(T):
        for x in range(T):
            if (x * 3 + y * 5 + tx) % 7 == 0:
                s.set_at((x, y), P["contorno"])
    for _ in range(5):
        s.set_at((rng.randrange(T), rng.randrange(4, T - 2)), P["roxo"])
    for x in range(T):                      # bordas de rocha
        s.set_at((x, 0), P["rocha_clara"] if x % 3 else P["rocha"])
        s.set_at((x, 1), P["rocha"])
        s.set_at((x, T - 1), P["rocha"] if x % 2 else P["rocha_clara"])
    return s


def _cave_entrance(tx, ty, left, right):
    s = _surface()
    s.fill(P["rocha"])
    for x in range(T):
        s.set_at((x, 0), P["rocha_clara"])
        s.set_at((x, T - 1), P["rocha_contorno"])
    for y in range(T):
        for x in range(T):
            if (x * 7 + y * 3) % 11 == 0:
                s.set_at((x, y), P["rocha_contorno"])
    # abertura escura em arco
    cx = 8
    for y in range(3, T):
        half = 6 if y > 6 else 4 + (y - 3) // 1
        for x in range(cx - half, cx + half):
            s.set_at((x, y), P["contorno"])
    for k, (x, y) in enumerate(((3, 12), (12, 9), (7, 13), (10, 12), (5, 8))):
        s.set_at((x, y), P["ceu"] if k % 2 else P["roxo"])   # cristais de quartzo
    return s


def _cave_wall(tx, ty, below_open):
    """Parede de caverna: topo escuro (bem distinto do piso); com chao abaixo, mostra a face frontal."""
    rng = random.Random(_h(tx, ty, 31))
    s = _surface()
    s.fill(P["rocha_contorno"])
    for _ in range(14):
        c = "contorno" if rng.random() < 0.55 else "rocha"
        s.set_at((rng.randrange(T), rng.randrange(T)), P[c])
    if below_open:
        for y in range(6, T):
            for x in range(T):
                c = "rocha" if (x * 3 + y) % 7 == 0 else "rocha_contorno"
                if y > 11:
                    c = "contorno" if (x + y) % 4 else "rocha_contorno"
                s.set_at((x, y), P[c])
        for x in range(T):
            s.set_at((x, 5), P["rocha_clara"])
            s.set_at((x, 6), P["rocha"])
    return s


def _crystal(tx, ty, floor):
    """Aglomerado de quartzo sobre o piso."""
    s = floor.copy()
    rng = random.Random(_h(tx, ty, 41))
    spikes = [(4, 13, 8), (8, 14, 11), (11, 13, 7)]
    for x, base, h in spikes:
        x += rng.randint(-1, 1)
        for k in range(h):
            y = base - k
            w = 2 if k < h - 3 else 1
            for dx in range(w):
                c = "branco" if (dx == 0 and k % 3 == 1) else ("ceu" if (x + k) % 2 else "roxo")
                s.set_at(((x + dx) % T, y % T), P[c])
        s.set_at((x % T, (base - h) % T), P["branco"])
    for x in range(2, 14):
        s.set_at((x, 14), P["contorno"])
    return s


def _exit_tile():
    s = _surface()
    s.fill(P["contorno"])
    for y in range(T):
        for x in range(2, T - 2):
            c = "branco" if y < 5 else ("ceu" if y < 11 else "agua_clara")
            if (x + y) % 5 or y > 11:
                s.set_at((x, y), P[c])
    return s


def _gate_tile(frame):
    s = _surface()
    s.fill(P["contorno"])
    for y in range(1, T - 1):
        for x in range(2, T - 2):
            d = abs(x - 7.5) + abs(y - 7.5) * 0.6
            if d < 6:
                c = "branco" if d < 2 + frame else ("roxo" if int(d) % 2 else "ceu")
                s.set_at((x, y), P[c])
    return s


def _tent(tx, ty, ground, left_open):
    """Barraca da resistencia (triangular, listrada) sobre o chao."""
    s = ground.copy()
    stripe = ("vermelho", "branco")
    for y in range(3, 15):
        half = (y - 2) * 0.62
        for x in range(T):
            if abs(x - 7.5) <= half:
                s.set_at((x, y), P[stripe[(x // 3) % 2] if y > 5 else "vermelho"])
    for y in range(8, 15):                  # entrada escura
        for x in range(6, 10):
            s.set_at((x, y), P["contorno"])
    for x in range(T):
        s.set_at((x, 15), P["chao_sombra"])
    s.set_at((7, 2), P["amarelo"]); s.set_at((8, 2), P["amarelo"]); s.set_at((7, 1), P["amarelo"])
    return s


def _thorns(tx, ty, ground):
    """Barreira de espinhos magicos (roxo e preto) que a Sombra Cinzenta ergueu."""
    rng = random.Random(_h(tx, ty, 51))
    s = ground.copy()
    for k in range(7):
        x = 1 + k * 2 + rng.randint(0, 1)
        h = rng.randint(8, 15)
        for j in range(h):
            xx = x + (1 if j % 5 == 4 else 0)
            s.set_at((xx % T, T - 1 - j), P["roxo"] if j % 3 else P["contorno"])
        s.set_at((x % T, T - h - 1), P["rosa_escuro"])
    return s


# --------------------------------------------------------------- agua
def _water(frame, tx, ty):
    s = _surface()
    s.fill(P["agua"])
    rng = random.Random(_h(tx, ty, 7))
    for _ in range(3):
        x, y = rng.randrange(T - 4), rng.randrange(T)
        shift = (frame * 2) % 4
        for k in range(3):
            _put(s, x + shift + k, y, "agua_clara")
        _put(s, x + shift - 1, y + 1, "agua_escura")
        _put(s, x + shift + 3, y + 1, "agua_escura")
    return s


# ================================================================= mapa
class MapArt:
    def __init__(self, world):
        self.world = world
        self.ground = [_ground_variant(i) for i in range(4)]
        self.path = [_path_base(i) for i in range(3)]
        self.tall = [_tall_grass_variant(0), _tall_grass_variant(1)]
        self.pines = [_big_pine(0), _big_pine(1)]
        self.rock = _rock()
        self.stone = [_stone_floor(i) for i in range(2)]
        self.flowers = [
            _flower("vermelho", "amarelo"), _flower("rosa", "amarelo"), _flower("branco", "amarelo"),
        ]

    def _kind(self, tx, ty):
        w = self.world
        if 0 <= tx < w.cols and 0 <= ty < w.rows:
            return w.grid[ty][tx]
        return None  # fora do mapa

    def _same(self, tx, ty, group):
        k = self._kind(tx, ty)
        return k is None or k in group  # fora do mapa conta como "igual" (sem borda)

    def _ground_tile(self, tx, ty):
        s = self.ground[_h(tx, ty) % 4].copy()
        if _h(tx, ty, 3) % 17 == 0:
            f = self.flowers[_h(tx, ty, 5) % 3]
            s.blit(f, (3 + _h(tx, ty, 9) % 9, 3 + _h(tx, ty, 11) % 9))
        return s

    def _path_tile(self, tx, ty):
        s = self.path[_h(tx, ty) % 3].copy()
        g = self.ground[_h(tx, ty, 1) % 4]
        grp = LAND_PATH
        n = self._same(tx, ty - 1, grp)
        e = self._same(tx + 1, ty, grp)
        so = self._same(tx, ty + 1, grp)
        w = self._same(tx - 1, ty, grp)

        def edge_px(x, y, depth):
            # borda irregular: o chao "entra" 1-2 px na trilha, com uma linha de sombra de areia
            wob = (x * 5 + y * 3 + tx * 2 + ty) % 4
            if depth == 0:
                return wob != 3
            if depth == 1:
                return wob == 0
            return False

        for y in range(T):
            for x in range(T):
                best = None
                for ok, d in ((n, y), (so, T - 1 - y), (w, x), (e, T - 1 - x)):
                    if not ok and d <= 1:
                        best = d if best is None else min(best, d)
                if best is not None:
                    if edge_px(x, y, best):
                        s.set_at((x, y), g.get_at((x, y)))
                    elif best == 1 or best == 0:
                        s.set_at((x, y), P["areia_sombra"])
        # cantos concavos (diagonal vazia com os dois lados de trilha)
        for dx, dy, cx, cy in ((-1, -1, 0, 0), (1, -1, T - 1, 0), (-1, 1, 0, T - 1), (1, 1, T - 1, T - 1)):
            if n and so and w and e and not self._same(tx + dx, ty + dy, grp):
                for ox in range(2):
                    for oy in range(2):
                        px = cx + (ox if cx == 0 else -ox)
                        py = cy + (oy if cy == 0 else -oy)
                        s.set_at((px, py), g.get_at((px, py)))
        return s

    def _stone_tile(self, tx, ty):
        """Piso de caverna com paredes em relevo onde faz fronteira com outro terreno."""
        s = self.stone[_h(tx, ty) % 2].copy()
        grp = {Terrain.STONE, Terrain.WALL, Terrain.CRYSTAL, Terrain.FISSURE, Terrain.EXIT, Terrain.GATE}
        n = self._same(tx, ty - 1, grp)
        so = self._same(tx, ty + 1, grp)
        w = self._same(tx - 1, ty, grp)
        e = self._same(tx + 1, ty, grp)
        if not n:                                  # parede do fundo (face alta)
            for x in range(T):
                s.set_at((x, 0), P["rocha_contorno"])
                for y in (1, 2):
                    s.set_at((x, y), P["rocha_clara"])
                for y in (3, 4, 5):
                    s.set_at((x, y), P["rocha"] if (x + y) % 5 else P["rocha_contorno"])
                s.set_at((x, 6), P["rocha_contorno"] if x % 2 else P["rocha"])
        if not so:
            for x in range(T):
                s.set_at((x, T - 1), P["rocha_contorno"])
                s.set_at((x, T - 2), P["rocha_clara"] if x % 3 else P["rocha"])
        for ok, xs in ((w, (0, 1)), (e, (T - 1, T - 2))):
            if not ok:
                for y in range(T):
                    s.set_at((xs[0], y), P["rocha_contorno"])
                    s.set_at((xs[1], y), P["rocha_clara"] if y % 3 else P["rocha"])
        return s

    def _water_tile(self, tx, ty, frame):
        s = _water(frame, tx, ty)
        for ok, y0, x0, horiz in (
            (self._same(tx, ty - 1, {Terrain.WATER}), 0, 0, True),
            (self._same(tx, ty + 1, {Terrain.WATER}), T - 1, 0, True),
            (self._same(tx - 1, ty, {Terrain.WATER}), 0, 0, False),
            (self._same(tx + 1, ty, {Terrain.WATER}), 0, T - 1, False),
        ):
            if ok:
                continue
            for k in range(T):
                px, py = (k, y0) if horiz else (x0, k)
                s.set_at((px, py), P["agua_clara"] if k % 3 else P["branco"])
        return s

    def render(self, frame):
        """Mapa inteiro (usado em testes e previas)."""
        return self.render_region(0, 0, self.world.cols, self.world.rows, frame)

    def render_region(self, x0, y0, cols, rows, frame):
        """Desenha so um retangulo de tiles [x0, x0+cols) x [y0, y0+rows) (um 'pedaco' do mapa)."""
        w = self.world
        surf = pygame.Surface((cols * T, rows * T))
        castle = {Terrain.CASTLE}
        for ty in range(y0, min(y0 + rows, w.rows)):
            for tx in range(x0, min(x0 + cols, w.cols)):
                kind = w.grid[ty][tx]
                if kind is Terrain.DIRT:
                    tile = self._path_tile(tx, ty)
                elif kind is Terrain.WATER:
                    tile = self._water_tile(tx, ty, frame)
                elif kind is Terrain.STONE:
                    tile = self._stone_tile(tx, ty)
                elif kind is Terrain.TENT:
                    tile = _tent(tx, ty, self._ground_tile(tx, ty), True)
                elif kind is Terrain.THORN:
                    tile = _thorns(tx, ty, self._ground_tile(tx, ty))
                elif kind is Terrain.CASTLE_WALL:
                    cw = {Terrain.CASTLE_WALL, Terrain.THORN}
                    top = self._kind(tx, ty - 1) not in cw
                    bottom = self._kind(tx, ty + 1) not in cw
                    tile = _castle(top, bottom, False)
                elif kind is Terrain.WALL:
                    below = self._kind(tx, ty + 1)
                    tile = _cave_wall(tx, ty, below is not None and below is not Terrain.WALL)
                elif kind is Terrain.CRYSTAL:
                    tile = _crystal(tx, ty, self._stone_tile(tx, ty))
                elif kind is Terrain.EXIT:
                    tile = _exit_tile()
                elif kind is Terrain.GATE:
                    tile = _gate_tile(frame)
                elif kind is Terrain.FISSURE:
                    tile = _fissure(tx, ty, True, True)
                elif kind is Terrain.CAVE:
                    tile = _cave_entrance(tx, ty, True, True)
                elif kind is Terrain.CASTLE:
                    top = not self._same(tx, ty - 1, castle) or self._kind(tx, ty - 1) is None
                    bottom = not self._same(tx, ty + 1, castle)
                    cols = [c for c in range(w.cols) if w.grid[ty][c] is Terrain.CASTLE]
                    mid = (min(cols) + max(cols)) // 2 if cols else -1
                    tile = _castle(top, bottom, door=(bottom and tx == mid))
                else:
                    tile = self._ground_tile(tx, ty)
                    if kind is Terrain.TALL_GRASS:
                        tile.blit(self.tall[(tx + ty) % 2], (0, 0))
                    elif kind is Terrain.TREE:
                        pine = self.pines[((tx // 2) + (ty // 2)) % 2]
                        tile.blit(pine[ty % 2][tx % 2], (0, 0))
                    elif kind is Terrain.ROCK:
                        on_road = any(self._kind(tx + dx, ty + dy) is Terrain.DIRT
                                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                        if on_road:                       # pedra sobre a estrada: base de terra
                            tile = self.path[_h(tx, ty) % 3].copy()
                        tile.blit(self.rock, (0, 0))
                surf.blit(tile, ((tx - x0) * T, (ty - y0) * T))
        return surf
