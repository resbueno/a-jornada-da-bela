"""Objetos interativos do mapa, lidos de um .objects.json.

kind:
  npc    : personagem; pode `joins` (vira amiga que segue a Bela), `gives` (transporte),
           `requires` (itens/amigas antes de ajudar) e `cutscene` (cena ao fim da conversa)
  sign   : placa
  pickup : coletavel (`item` vira uma marca no inventario)
  task   : obstaculo invisivel resolvido em etapas (`steps`), ex.: espinheiro; `clear` libera tiles
  prop   : objeto grande com imagem (Maria Fumaca, dragao); ocupa `size` tiles e tambem tem `steps`
"""
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

import pygame

from src import config
from src.world.tilemap import ROOT

T = config.TILE
P = config.PALETTE
KINDS = ("npc", "sign", "pickup", "task", "prop")


@dataclass
class Step:
    needs: list
    sets: str
    lines: list
    missing: list


@dataclass
class Interactable:
    kind: str
    tile: tuple               # (tx, ty) do canto de cima a esquerda
    name: str
    lines: list = field(default_factory=list)
    gives: str = None         # transporte entregue ao fim da 1a conversa
    after: list = field(default_factory=list)  # falas depois de ajudar
    given: bool = False
    sprite: str = None        # personagem em assets/sprites (ex.: lana_bosque)
    requires: list = field(default_factory=list)  # itens/amigas necessarios para a conversa avancar
    missing: list = field(default_factory=list)   # falas enquanto falta algo
    item: str = None          # coletavel: marca concedida ao pegar
    anim: bool = False        # sprite em loop (0-1-2-1), sempre de frente (treino com pesos)
    joins: str = None         # amiga que entra no grupo ao fim da conversa
    cutscene: str = None      # cena que comeca quando tudo estiver feito
    steps: list = field(default_factory=list)     # etapas de um obstaculo (Step)
    clear: tuple = None       # (x0, y0, x1, y1): tiles liberados quando o obstaculo e resolvido
    size: tuple = (1, 1)      # tiles ocupados (objetos grandes)
    image: str = None         # folha de sprites de um objeto grande
    image_w: int = 0          # largura de cada quadro da folha
    scared: bool = False      # treme de medo (o unicornio perdido)
    snore: bool = False       # ronca (o dragao)
    done: bool = False

    @property
    def rect(self):
        return pygame.Rect(self.tile[0] * T, self.tile[1] * T, self.size[0] * T, self.size[1] * T)

    def footprint(self):
        x0, y0 = self.tile
        return [(x0 + dx, y0 + dy) for dy in range(self.size[1]) for dx in range(self.size[0])]

    def covers(self, tile):
        if tile in self.footprint():
            return True
        if self.clear and not self.done:
            x0, y0, x1, y1 = self.clear
            return x0 <= tile[0] <= x1 and y0 <= tile[1] <= y1
        return False

    @property
    def solid(self):
        return self.kind in ("npc", "sign", "prop")

    def blocked(self, have):
        return any(r not in have for r in self.requires)

    def current_lines(self, have=frozenset()):
        if self.blocked(have) and self.missing and not self.given:
            return self.missing
        return self.after if (self.given and self.after) else self.lines

    def next_step(self, have):
        """Primeira etapa ainda nao feita (ou None)."""
        for st in self.steps:
            if st.sets and st.sets not in have:
                return st
            if not st.sets:
                return st
        return None

    # ------------------------------------------------------------ desenho
    def draw(self, canvas, camera, near=None, ticks=0):
        x, y = self.rect.x - camera.x, self.rect.y - camera.y
        if self.kind == "task":
            return
        if self.kind == "sign":
            _sign(canvas, x, y)
        elif self.kind == "pickup":
            _pickup(canvas, x, y, self.item, ticks)
        elif self.image:
            from src.sprites import frames
            sheet = frames(self.image, self.image_w)
            if self.snore:
                img = sheet[(ticks // 50) % 2]
            else:
                img = sheet[(ticks // 30) % len(sheet)] if self.kind != "npc" else sheet[0]
            w, h = self.rect.size
            ox = x + (w - img.get_width()) // 2
            oy = y + h - img.get_height()
            if self.scared:
                ox += 1 if (ticks // 3) % 2 else -1
            if self.kind == "npc" and near is not None and near[0] > self.rect.centerx:
                from src.sprites import flipped
                img = flipped(img)
            canvas.blit(img, (ox, oy + (8 if self.size == (1, 1) else 0)))
            if self.snore:
                _zzz(canvas, x + 34, y + 16, ticks)
            if self.scared and (ticks // 40) % 2:
                pygame.draw.circle(canvas, P["agua_clara"], (x + 4, y - 18), 3)   # lagrimazinha
        elif self.sprite:
            from src.sprites import SPRITE_H, character
            if self.anim:                                      # levantando peso: cicla os quadros
                step = (ticks // 21 + self.tile[0]) % 4
                canvas.blit(character(self.sprite)["down"][(0, 1, 2, 1)[step]], (x, y + T - SPRITE_H))
                return
            facing = "down"
            if near is not None:                               # olha para a Bela quando ela esta perto
                dx = near[0] - self.rect.centerx
                dy = near[1] - self.rect.centery
                if abs(dx) < 112 and abs(dy) < 112:
                    if abs(dx) > abs(dy):
                        facing = "right" if dx > 0 else "left"
                    else:
                        facing = "down" if dy > 0 else "up"
            breathe = 2 if (ticks // 36) % 2 else 0
            canvas.blit(character(self.sprite)[facing][0], (x, y + T - SPRITE_H - breathe))


def _sign(canvas, x, y):
    pygame.draw.rect(canvas, P["madeira_escura"], (x + 13, y + 14, 6, 18))
    pygame.draw.rect(canvas, P["contorno"], (x + 2, y + 2, 28, 16))
    pygame.draw.rect(canvas, P["madeira"], (x + 4, y + 4, 24, 12))
    pygame.draw.rect(canvas, P["areia"], (x + 4, y + 4, 24, 2))
    for k in range(3):
        pygame.draw.rect(canvas, P["madeira_escura"], (x + 7, y + 8 + k * 3, 18 - k * 5, 1))


def _pickup(canvas, x, y, item, ticks):
    bob = round(math.sin(ticks / 12.0) * 2)
    y += bob
    pygame.draw.ellipse(canvas, P["chao_sombra"], (x + 6, y + 24 - bob, 20, 6))
    if item == "tabuas":
        for k, c in enumerate(("madeira", "madeira_escura", "madeira")):
            pygame.draw.rect(canvas, P["contorno"], (x + 3, y + 8 + k * 5, 26, 6))
            pygame.draw.rect(canvas, P[c], (x + 4, y + 9 + k * 5, 24, 4))
    elif item == "blocos":
        for k, (bx, by, c) in enumerate(((4, 14, "vermelho"), (16, 14, "azul"), (10, 4, "amarelo"))):
            pygame.draw.rect(canvas, P["contorno"], (x + bx, y + by, 12, 10))
            pygame.draw.rect(canvas, P[c], (x + bx + 1, y + by + 1, 10, 8))
            pygame.draw.rect(canvas, P["branco"], (x + bx + 3, y + by - 1, 3, 2))
    elif item == "vela":
        pygame.draw.polygon(canvas, P["contorno"], [(x + 6, y + 26), (x + 6, y + 2), (x + 28, y + 26)])
        pygame.draw.polygon(canvas, P["branco"], [(x + 8, y + 24), (x + 8, y + 6), (x + 24, y + 24)])
        pygame.draw.rect(canvas, P["rosa"], (x + 8, y + 14, 8, 3))
    else:
        pygame.draw.circle(canvas, P["amarelo"], (x + 16, y + 14), 7)
    if (ticks // 20) % 2:                                      # brilho: chama a atencao
        canvas.fill(P["branco"], (x + 26, y + 2, 3, 3))
        canvas.fill(P["branco"], (x + 27, y + 1, 1, 5))


def _zzz(canvas, x, y, ticks):
    from src.text import draw_text
    for k in range(3):
        t = (ticks + k * 40) % 120
        draw_text(canvas, "z" if k < 2 else "Z", x - t // 4 - k * 6, y - t // 2 - k * 4,
                  P["branco"], size=16 + k * 16, shadow=P["contorno"])


def load_objects(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for i, e in enumerate(data):
        if e.get("kind") not in KINDS:
            raise ValueError(f"{path.name}[{i}]: kind desconhecido '{e.get('kind')}'")
        req = e.get("requires") or []
        out.append(Interactable(
            kind=e["kind"], tile=tuple(e["tile"]), name=e.get("name", ""), lines=list(e.get("lines", [])),
            gives=e.get("gives"), after=list(e.get("after", [])), sprite=e.get("sprite"),
            requires=[req] if isinstance(req, str) else list(req), missing=list(e.get("missing", [])),
            item=e.get("item"), anim=bool(e.get("anim", False)), joins=e.get("joins"),
            cutscene=e.get("cutscene"), clear=tuple(e["clear"]) if e.get("clear") else None,
            steps=[Step(list(s.get("needs", [])), s.get("sets", ""), list(s.get("lines", [])),
                        list(s.get("missing", []))) for s in e.get("steps", [])],
            size=tuple(e.get("size", (1, 1))), image=e.get("image"), image_w=int(e.get("image_w", 0)),
            scared=bool(e.get("scared", False)), snore=bool(e.get("snore", False)),
        ))
    return out


def load_decor(path):
    """Enfeites de um .decor.json: lista de {"kind": ..., "tile": [x, y]}."""
    from src.entities.decor import KINDS as DECOR

    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    out = []
    for i, entry in enumerate(json.loads(path.read_text(encoding="utf-8"))):
        kind = entry.get("kind")
        if kind not in DECOR:
            raise ValueError(f"{path.name}[{i}]: kind desconhecido '{kind}'")
        out.append(DECOR[kind](tuple(entry["tile"]), phase=i * 37))
    return out
