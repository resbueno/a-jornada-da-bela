"""Objetos interativos do mapa (NPCs e placas), lidos de um .objects.json."""
import json
from dataclasses import dataclass, field
from pathlib import Path

import pygame

from src import config
from src.world.tilemap import ROOT

T = config.TILE
COLORS = {"npc": "lilas_magia", "sign": "tronco_terra"}


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

    @property
    def rect(self):
        return pygame.Rect(self.tile[0] * T, self.tile[1] * T, T, T)

    def current_lines(self):
        return self.after if (self.given and self.after) else self.lines

    def draw(self, canvas, camera):
        x, y = self.rect.x - camera.x, self.rect.y - camera.y
        color = config.PALETTE[COLORS[self.kind]]
        if self.kind == "sign":
            pygame.draw.rect(canvas, color, (x + 6, y + 8, 4, 8))
            pygame.draw.rect(canvas, config.PALETTE["madeira_terra_clara"], (x + 2, y + 2, 12, 7))
        elif self.sprite:
            from src.sprites import SPRITE_H, character
            canvas.blit(character(self.sprite)["down"][0], (x, y + T - SPRITE_H))
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
    from src.entities.creatures import Eel

    path = Path(path)
    if not path.is_absolute():
        path = ROOT / path
    out = []
    for i, entry in enumerate(json.loads(path.read_text(encoding="utf-8"))):
        if entry.get("kind") != "eel":
            raise ValueError(f"{path.name}[{i}]: kind desconhecido '{entry.get('kind')}'")
        out.append(Eel(tuple(entry["tile"]), tuple(entry["range"])))
    return out
