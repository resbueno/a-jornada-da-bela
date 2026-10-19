"""Mapa em grade de tiles, carregado de um .map.txt."""
from pathlib import Path

import pygame

from src import config
from src.world.terrain import GLYPHS, Terrain

ROOT = Path(__file__).resolve().parents[2]


class Tilemap:
    def __init__(self, grid):
        self.grid = grid                # lista de linhas; cada linha e uma lista de Terrain
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.pixel_w = self.cols * config.TILE
        self.pixel_h = self.rows * config.TILE
        self.solid_tiles = set()        # tiles ocupados por objetos (NPCs, placas)
        self.style = "vale"             # estilo da arte do chao (bosque, vale, montanha, castelo)
        self._art = None                # gerador de arte (criado na primeira vez que desenha)
        self._chunks = {}               # (cx, cy, quadro) -> Surface de CHUNK x CHUNK tiles

    @classmethod
    def load(cls, path):
        """Le um .map.txt. Linhas vazias e linhas iniciadas por ';' sao ignoradas."""
        path = Path(path)
        if not path.is_absolute():
            path = ROOT / path
        grid = []
        for n, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = raw.rstrip()
            if not line or line.startswith(";"):
                continue
            row = []
            for col, ch in enumerate(line, 1):
                if ch not in GLYPHS:
                    raise ValueError(f"{path.name}:{n}:{col}: glifo desconhecido '{ch}'")
                row.append(GLYPHS[ch])
            if grid and len(row) != len(grid[0]):
                raise ValueError(f"{path.name}:{n}: largura {len(row)} != {len(grid[0])}")
            grid.append(row)
        if not grid:
            raise ValueError(f"{path.name}: mapa vazio")
        return cls(grid)

    def terrain_at(self, tx, ty):
        """Terreno do tile (tx, ty). Fora do mapa conta como arvore (bloqueia)."""
        if 0 <= tx < self.cols and 0 <= ty < self.rows:
            return self.grid[ty][tx]
        return Terrain.TREE

    def terrain_at_pixel(self, px, py):
        return self.terrain_at(int(px) // config.TILE, int(py) // config.TILE)

    CHUNK = 8  # tiles por lado de cada pedaco desenhado sob demanda

    def invalidate(self):
        """Descarta a arte em cache (ex.: depois de mudar tiles durante uma cena)."""
        self._chunks.clear()
        if self._art is not None:
            from src.world.tileart import MapArt
            cache = self._art.cache
            self._art = MapArt(self, self.style)
            self._art.cache = {k: v for k, v in cache.items() if k[0] in ("ground", "tall", "flowers")}

    def set_tiles(self, x0, y0, x1, y1, old, new):
        """Troca o terreno `old` por `new` no retangulo e redesenha."""
        for y in range(max(y0, 0), min(y1, self.rows - 1) + 1):
            for x in range(max(x0, 0), min(x1, self.cols - 1) + 1):
                if self.grid[y][x] is old:
                    self.grid[y][x] = new
        self.invalidate()

    def draw(self, canvas, camera, frame=0):
        """Desenha so os pedacos visiveis; cada um e criado na 1a vez e reaproveitado (2 quadros de agua)."""
        if self._art is None:
            from src.world.tileart import MapArt  # import local: pede o display ja iniciado
            self._art = MapArt(self, self.style)
        t = config.TILE
        size = self.CHUNK * t
        f = frame % 2
        max_cx = (self.cols - 1) // self.CHUNK
        max_cy = (self.rows - 1) // self.CHUNK
        cx0 = max(camera.x // size, 0)
        cy0 = max(camera.y // size, 0)
        cx1 = min((camera.x + config.LOGICAL_W - 1) // size, max_cx)
        cy1 = min((camera.y + config.LOGICAL_H - 1) // size, max_cy)
        for cy in range(cy0, cy1 + 1):
            for cx in range(cx0, cx1 + 1):
                key = (cx, cy, f)
                surf = self._chunks.get(key)
                if surf is None:
                    surf = self._art.render_region(cx * self.CHUNK, cy * self.CHUNK, self.CHUNK, self.CHUNK, f)
                    self._chunks[key] = surf
                canvas.blit(surf, (cx * size - camera.x, cy * size - camera.y))
