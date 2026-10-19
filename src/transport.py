"""Transportes: terrenos permitidos e velocidade de cada um (ver DESIGN.md)."""
from dataclasses import dataclass

from src.world.terrain import WATERS, Terrain

LAND = frozenset({Terrain.GRASS, Terrain.TALL_GRASS, Terrain.DIRT, Terrain.STONE, Terrain.WIND, Terrain.RAIL,
                  Terrain.PLANKS, Terrain.GATE, Terrain.FLOWERS})


@dataclass(frozen=True)
class Transport:
    key: str
    name: str
    terrains: frozenset
    speed: float  # px/s

    def can_enter(self, terrain):
        return terrain in self.terrains


# velocidades (tela de 640x360): a pe 120, barco 150, unicornio 180 px/s
ON_FOOT = Transport("on_foot", "A pé", LAND, 120.0)
UNICORN = Transport("unicorn", "Unicórnio", LAND, 180.0)
BOAT = Transport("boat", "Barco", WATERS, 150.0)

ALL = {t.key: t for t in (ON_FOOT, UNICORN, BOAT)}
