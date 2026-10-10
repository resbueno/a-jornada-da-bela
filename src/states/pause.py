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
    Terrain.GRASS: "chao", Terrain.TALL_GRASS: "verde_escuro", Terrain.DIRT: "areia",
    Terrain.STONE: "rocha", Terrain.WATER: "agua", Terrain.TREE: "verde_medio",
    Terrain.ROCK: "rocha_clara", Terrain.FISSURE: "contorno", Terrain.CAVE: "roxo",
    Terrain.WALL: "rocha_contorno", Terrain.CRYSTAL: "ceu", Terrain.EXIT: "branco",
    Terrain.GATE: "roxo", Terrain.TENT: "vermelho", Terrain.THORN: "roxo",
    Terrain.CASTLE_WALL: "rocha_clara", Terrain.CASTLE: "rocha_clara",
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
        top = 6
        if self.mini is not None:
            mw, mh = self.mini.get_size()
            scale = 1
            if mw * 2 <= config.LOGICAL_W - 40 and mh * 2 <= 90:
                scale = 2                                   # mapas pequenos ficam em 2x
            surf = pygame.transform.scale(self.mini, (mw * scale, mh * scale)) if scale > 1 else self.mini
            sw, sh = surf.get_size()
            mx = (config.LOGICAL_W - sw) // 2
            draw_panel(canvas, (mx - 3, top - 3, sw + 6, sh + 6))
            canvas.blit(surf, (mx, top))
            if (self.ticks // 15) % 2 == 0:                  # a Isabela pisca no mapa
                t = config.TILE
                cx, cy = self.play.player.center
                px, py = mx + int(cx / t * scale), top + int(cy / t * scale)
                pygame.draw.rect(canvas, p["contorno"], (px - 2, py - 2, 5, 5))
                pygame.draw.rect(canvas, p["rosa"], (px - 1, py - 1, 3, 3))
            for obj in self.play.objects:                    # personagens (ponto amarelo)
                if obj.kind == "npc":
                    nx = mx + int(obj.rect.centerx / config.TILE * scale)
                    ny = top + int(obj.rect.centery / config.TILE * scale)
                    canvas.fill(p["amarelo"], (nx - 1, ny - 1, 2, 2))
            top += sh + 14
        w, h = 170, 30 + len(ENTRIES) * 14 + 10
        rect = ((config.LOGICAL_W - w) // 2, min(top, config.LOGICAL_H - h - 2), w, h)
        draw_menu(canvas, rect, "PAUSA", ENTRIES, self.cursor)
