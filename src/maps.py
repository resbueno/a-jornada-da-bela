"""Registro dos mapas do jogo e das passagens entre eles."""
from src.world.terrain import Terrain

MAPS = {
    "floresta_inicial": dict(
        base="assets/maps/floresta_inicial", spawn=(24, 15), weather="rain", dark=False, card=None),
    "cavernas": dict(
        base="assets/maps/cavernas", spawn=(3, 20), weather="none", dark=True,
        card="Capítulo 3: As Cavernas de Quartzo"),
    "estrada": dict(
        base="assets/maps/estrada", spawn=(3, 10), weather="none", dark=False, tint="sunset", timer=30, timer_end_x=133,
        card="Capítulo 4: A Estrada do Pôr do Sol"),
    "portoes": dict(
        base="assets/maps/portoes", spawn=(18, 20), weather="none", dark=False, tint="sunset",
        card="Os Portões do Castelo"),
}

# (mapa atual, terreno pisado) -> (mapa de destino, tile de chegada ou None = padrao do destino)
TRANSITIONS = {
    ("floresta_inicial", Terrain.CAVE): ("cavernas", None),
    ("cavernas", Terrain.EXIT): ("floresta_inicial", (40, 5)),
    ("cavernas", Terrain.GATE): ("estrada", None),
    ("estrada", Terrain.GATE): ("portoes", None),
}
