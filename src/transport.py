"""Transportes: terrenos permitidos e velocidade de cada um (ver DESIGN.md)."""
from dataclasses import dataclass

from src.world.terrain import Terrain

LAND = frozenset({Terrain.GRASS, Terrain.TALL_GRASS, Terrain.DIRT, Terrain.STONE, Terrain.CASTLE, Terrain.CAVE,
                  Terrain.EXIT, Terrain.GATE})


@dataclass(frozen=True)
class Transport:
    key: str
    name: str
    terrains: frozenset
    speed: float  # px/s

    def can_enter(self, terrain):
        return terrain in self.terrains


# velocidades: normal 60, media 75, rapida 90 px/s
ON_FOOT = Transport("on_foot", "A pé", LAND, 60.0)
UNICORN = Transport("unicorn", "Unicórnio", LAND, 90.0)
BOAT = Transport("boat", "Barco", frozenset({Terrain.WATER}), 75.0)
PINK_CAR = Transport("pink_car", "Carro rosa", frozenset({Terrain.DIRT}), 90.0)

ALL = {t.key: t for t in (ON_FOOT, UNICORN, BOAT, PINK_CAR)}
