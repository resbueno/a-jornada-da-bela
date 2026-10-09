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
        self._frames = None             # arte pre-renderizada (2 quadros de agua)

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

    def draw(self, canvas, camera, frame=0):
        """Recorta da arte pre-renderizada a regiao visivel. frame alterna a agua (0/1)."""
        if self._frames is None:
            from src.world.tileart import MapArt  # import local: pede o display ja iniciado
            art = MapArt(self)
            self._frames = [art.render(0), art.render(1)]
        view = pygame.Rect(camera.x, camera.y, config.LOGICAL_W, config.LOGICAL_H)
        src = self._frames[frame % 2]
        clip = view.clip(src.get_rect())
        canvas.blit(src, (clip.x - camera.x, clip.y - camera.y), clip)
