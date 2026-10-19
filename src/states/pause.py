"""Estado Pausa: minimapa do mundo e menu (continuar ou voltar ao titulo)."""
import pygame

from src import config
from src.input import Action
from src.states.base import State
from src.ui import draw_menu, draw_panel
from src.world.terrain import Terrain

ENTRIES = ["Continuar", "Sair para o título"]

# cor de cada terreno no minimapa (papel da paleta)
MINI_COLORS = {
    Terrain.GRASS: "chao", Terrain.TALL_GRASS: "verde_medio", Terrain.DIRT: "areia", Terrain.FLOWERS: "rosa",
    Terrain.STONE: "rocha_clara", Terrain.WATER: "agua", Terrain.RAPIDS: "agua_clara", Terrain.TREE: "verde_escuro",
    Terrain.ROCK: "rocha", Terrain.FISSURE: "contorno", Terrain.THORN: "roxo", Terrain.CLIFF: "rocha_contorno",
    Terrain.WIND: "branco", Terrain.RAIL: "madeira_escura", Terrain.PLANKS: "madeira", Terrain.POST: "madeira",
    Terrain.LAMP: "amarelo", Terrain.CASTLE_WALL: "rocha_clara", Terrain.CASTLE_GATE: "madeira_escura",
    Terrain.GATE: "amarelo",
}


class Pause(State):
    overlay = True

    def __init__(self, play=None):
        super().__init__()
        self.cursor = 0
        self.play = play
        self.mini = self._build_minimap() if play is not None else None
        self.ticks = 0

    def _build_minimap(self):
        w = self.play.world
        surf = pygame.Surface((w.cols, w.rows))
        for y in range(w.rows):
            row = w.grid[y]
            for x in range(w.cols):
                surf.set_at((x, y), config.PALETTE[MINI_COLORS.get(row[x], "chao")])
        return surf

    def update(self, dt, inp):
        self.ticks += 1
        if inp.pressed(Action.PAUSE):
            self.manager.pop()
        elif inp.pressed(Action.UP):
            self.cursor = (self.cursor - 1) % len(ENTRIES)
        elif inp.pressed(Action.DOWN):
            self.cursor = (self.cursor + 1) % len(ENTRIES)
        elif inp.pressed(Action.INTERACT):
            if self.cursor == 0:
                self.manager.pop()
            else:
                from src.states.title import Title  # import local: evita ciclo Title <-> Play <-> Pause
                self.manager.change(Title())

    def draw(self, canvas):
        p = config.PALETTE
        top = 12
        W, H = config.LOGICAL_W, config.LOGICAL_H
        if self.mini is not None:
            mw, mh = self.mini.get_size()
            scale = max(1, min(4, (W - 80) // mw, 180 // mh))
            surf = pygame.transform.scale(self.mini, (mw * scale, mh * scale))
            sw, sh = surf.get_size()
            mx = (W - sw) // 2
            draw_panel(canvas, (mx - 8, top - 8, sw + 16, sh + 16))
            canvas.blit(surf, (mx, top))
            t = config.TILE
            for obj in self.play.objects:                    # personagens (ponto amarelo)
                if obj.kind == "npc":
                    nx = mx + int(obj.rect.centerx / t * scale)
                    ny = top + int(obj.rect.centery / t * scale)
                    canvas.fill(p["amarelo"], (nx - 2, ny - 2, 4, 4))
            if (self.ticks // 15) % 2 == 0:                  # a Bela pisca no mapa
                cx, cy = self.play.player.center
                px, py = mx + int(cx / t * scale), top + int(cy / t * scale)
                pygame.draw.rect(canvas, p["contorno"], (px - 4, py - 4, 9, 9))
                pygame.draw.rect(canvas, p["rosa"], (px - 3, py - 3, 7, 7))
            top += sh + 24
        w, h = 340, 60 + len(ENTRIES) * 32 + 10
        rect = ((W - w) // 2, min(top, H - h - 4), w, h)
        draw_menu(canvas, rect, "PAUSA", ENTRIES, self.cursor)
