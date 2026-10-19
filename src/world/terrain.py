"""Tipos de terreno. Cada glifo do .map.txt vira um Terrain."""
from enum import Enum


class Terrain(Enum):
    GRASS = "grass"            # grama
    TALL_GRASS = "tall_grass"  # grama alta (so enfeite: da para andar)
    DIRT = "dirt"              # terra / trilha
    STONE = "stone"            # piso de pedra (patio do castelo, plataforma)
    WATER = "water"            # agua funda (so o barco)
    RAPIDS = "rapids"          # corredeira: agua que empurra o barco rio abaixo
    TREE = "tree"              # arvore (pinheiro 2x2): sempre bloqueia
    ROCK = "rock"              # pedra grande: sempre bloqueia (tambem no meio do rio)
    FISSURE = "fissure"        # desfiladeiro: ninguem entra; o unicornio salta por cima
    THORN = "thorn"            # espinheiro magico: bloqueia ate a Lana puxar os galhos
    CLIFF = "cliff"            # paredao de rocha da montanha: bloqueia
    WIND = "wind"              # trilha de vento forte: da para pisar, mas o vento empurra de volta
    RAIL = "rail"              # trilhos da Maria Fumaca
    PLANKS = "planks"          # tabuas de madeira (cais, plataforma da estacao, ponte)
    POST = "post"              # pilar da ponte antiga, quebrada: bloqueia
    LAMP = "lamp"              # poste com lampiao (ilumina o bosque): bloqueia
    CASTLE_WALL = "castle_wall"  # muralha do castelo: bloqueia
    CASTLE_GATE = "castle_gate"  # portao do castelo (fechado): bloqueia
    GATE = "gate"              # passagem para o proximo mapa
    FLOWERS = "flowers"        # canteiro de flores (enfeite, da para andar)


GLYPHS = {
    "g": Terrain.GRASS,
    "h": Terrain.TALL_GRASS,
    "d": Terrain.DIRT,
    "s": Terrain.STONE,
    "~": Terrain.WATER,
    "v": Terrain.RAPIDS,
    "#": Terrain.TREE,
    "r": Terrain.ROCK,
    "x": Terrain.FISSURE,
    "Y": Terrain.THORN,
    "W": Terrain.CLIFF,
    "w": Terrain.WIND,
    "=": Terrain.RAIL,
    "k": Terrain.PLANKS,
    "p": Terrain.POST,
    "L": Terrain.LAMP,
    "K": Terrain.CASTLE_WALL,
    "C": Terrain.CASTLE_GATE,
    "G": Terrain.GATE,
    "f": Terrain.FLOWERS,
}

WATERS = frozenset({Terrain.WATER, Terrain.RAPIDS})
