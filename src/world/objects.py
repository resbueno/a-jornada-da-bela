"""Objetos interativos do mapa (NPCs e placas), lidos de um .objects.json."""
import json
from dataclasses import dataclass, field
from pathlib import Path

import pygame

from src import config
from src.world.tilemap import ROOT

T = config.TILE
COLORS = {"npc": "lilas_magia", "sign": "tronco_terra", "altar": "rocha_clara", "pickup": "madeira"}


@dataclass
class Interactable:
    kind: str                 # "npc" ou "sign"
    tile: tuple               # (tx, ty)
    name: str
    lines: list
    gives: str = None         # chave de transporte entregue ao fim da 1a conversa
    after: list = field(default_factory=list)  # falas depois de entregar
    given: bool = False
    sprite: str = None        # nome do personagem em assets/sprites (ex.: olivia)
    requires: str = None      # item (flag) que o jogador precisa ter para a conversa avancar
    missing: list = field(default_factory=list)  # falas enquanto o item nao foi trazido
    item: str = None          # coletavel: flag concedida ao pegar

    @property
    def rect(self):
        return pygame.Rect(self.tile[0] * T, self.tile[1] * T, T, T)

    def blocked(self, flags):
        return bool(self.requires) and self.requires not in flags

    def current_lines(self, flags=frozenset()):
        if self.blocked(flags) and self.missing:
            return self.missing
        return self.after if (self.given and self.after) else self.lines

    def draw(self, canvas, camera, near=None):
        x, y = self.rect.x - camera.x, self.rect.y - camera.y
        color = config.PALETTE[COLORS[self.kind]]
        if self.kind == "sign":
            pygame.draw.rect(canvas, color, (x + 6, y + 8, 4, 8))
            pygame.draw.rect(canvas, config.PALETTE["madeira_terra_clara"], (x + 2, y + 2, 12, 7))
        elif self.kind == "pickup":                      # remo do barco no chao
            for k in range(11):
                pygame.draw.rect(canvas, config.PALETTE["madeira"], (x + 3 + k, y + 12 - k, 2, 2))
            pygame.draw.rect(canvas, config.PALETTE["madeira_escura"], (x + 1, y + 12, 4, 3))
            pygame.draw.rect(canvas, config.PALETTE["madeira"], (x + 11, y + 1, 4, 4))
            if (pygame.time.get_ticks() // 400) % 2:       # brilho: chama a atencao
                canvas.fill(config.PALETTE["branco"], (x + 13, y, 2, 2))
        elif self.kind == "altar":
            pygame.draw.rect(canvas, config.PALETTE["rocha_contorno"], (x + 1, y + 6, 14, 10))
            pygame.draw.rect(canvas, config.PALETTE["rocha_clara"], (x + 2, y + 5, 12, 4))
            pygame.draw.rect(canvas, config.PALETTE["rocha"], (x + 2, y + 9, 12, 6))
            for k, c in enumerate(("agua", "rosa", "vermelho", "verde_brilho")):
                pygame.draw.rect(canvas, config.PALETTE[c], (x + 3 + k * 3, y + 6, 2, 2))
            pygame.draw.rect(canvas, config.PALETTE["branco"], (x + 7, y + 2, 2, 3))
        elif self.sprite:
            from src.sprites import SPRITE_H, character
            facing = "down"
            if near is not None:                               # olha para a Isabela quando ela esta perto
                dx = near[0] - (self.rect.centerx)
                dy = near[1] - (self.rect.centery)
                if abs(dx) < 56 and abs(dy) < 56:
                    if abs(dx) > abs(dy):
                        facing = "right" if dx > 0 else "left"
                    else:
                        facing = "down" if dy > 0 else "up"
            breathe = 1 if (pygame.time.get_ticks() // 600) % 2 else 0   # respira: sobe 1 px
            canvas.blit(character(self.sprite)[facing][0], (x, y + T - SPRITE_H - breathe))
        else:
            pygame.draw.rect(canvas, color, (x, y, T, T))


def load_objects(path):
    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    data = json.loads(path.read_text(encoding="utf-8"))
    out = []
    for i, entry in enumerate(data):
        try:
            out.append(Interactable(
                kind=entry["kind"],
                tile=tuple(entry["tile"]),
                name=entry.get("name", ""),
                lines=list(entry["lines"]),
                gives=entry.get("gives"),
                after=list(entry.get("after", [])),
                sprite=entry.get("sprite"),
                requires=entry.get("requires"),
                missing=list(entry.get("missing", [])),
                item=entry.get("item"),
            ))
        except KeyError as e:
            raise ValueError(f"{path.name}[{i}]: campo ausente {e}") from None
        if out[-1].kind not in COLORS:
            raise ValueError(f"{path.name}[{i}]: kind desconhecido '{out[-1].kind}'")
    return out


def load_decor(path):
    """Decorativos de um .decor.json: lista de {"kind": ..., "tile": [x, y]}."""
    from src.entities.decor import KINDS

    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    out = []
    for i, entry in enumerate(json.loads(path.read_text(encoding="utf-8"))):
        kind = entry.get("kind")
        if kind not in KINDS:
            raise ValueError(f"{path.name}[{i}]: kind desconhecido '{kind}'")
        out.append(KINDS[kind](tuple(entry["tile"]), phase=i * 37))
    return out


def load_creatures(path):
    """Criaturas de um .creatures.json: [{"kind": "eel", "tile": [x, y], "range": [x0, x1]}]."""
    from src.entities.creatures import Eel, Minion

    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    out = []
    for i, entry in enumerate(json.loads(path.read_text(encoding="utf-8"))):
        kind = entry.get("kind")
        if kind == "eel":
            out.append(Eel(tuple(entry["tile"]), tuple(entry["range"])))
        elif kind == "minion":
            out.append(Minion(tuple(entry["tile"]), tuple(entry["range"])))
        else:
            raise ValueError(f"{path.name}[{i}]: kind desconhecido '{kind}'")
    return out
