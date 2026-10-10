"""Tipos de terreno. Cada glifo do .map.txt vira um Terrain."""
from enum import Enum


class Terrain(Enum):
    GRASS = "grass"            # grama
    TALL_GRASS = "tall_grass"  # grama alta (carro nao entra)
    DIRT = "dirt"              # terra / caminho
    STONE = "stone"            # pedra (piso de caverna)
    WATER = "water"            # agua funda (so o barco)
    TREE = "tree"              # arvore / parede: sempre bloqueia
    CASTLE = "castle"          # castelo: chegar aqui e a vitoria
    ROCK = "rock"              # pedra grande: sempre bloqueia
    FISSURE = "fissure"        # fenda: ninguem entra; o unicornio salta por cima
    CAVE = "cave"              # entrada da caverna: leva ao mapa das cavernas
    WALL = "wall"              # parede de caverna: sempre bloqueia
    CRYSTAL = "crystal"        # cristal de quartzo: bloqueia e ilumina
    EXIT = "exit"              # saida da caverna de volta ao mapa anterior
    GATE = "gate"              # portal do fim do capitulo


GLYPHS = {
    "g": Terrain.GRASS,
    "h": Terrain.TALL_GRASS,
    "d": Terrain.DIRT,
    "s": Terrain.STONE,
    "~": Terrain.WATER,
    "#": Terrain.TREE,
    "C": Terrain.CASTLE,
    "r": Terrain.ROCK,
    "x": Terrain.FISSURE,
    "E": Terrain.CAVE,
    "W": Terrain.WALL,
    "q": Terrain.CRYSTAL,
    "O": Terrain.EXIT,
    "G": Terrain.GATE,
}

# Cor provisoria de cada terreno (papel da paleta) ate existirem os sprites
COLORS = {
    Terrain.GRASS: "grama",
    Terrain.TALL_GRASS: "folha_escura",
    Terrain.DIRT: "madeira_terra_clara",
    Terrain.STONE: "pedra_escura",
    Terrain.WATER: "agua_lago",
    Terrain.TREE: "folha_escura",
    Terrain.CASTLE: "pedra_clara",
    Terrain.ROCK: "pedra_escura",
    Terrain.FISSURE: "contorno",
    Terrain.CAVE: "pedra_escura",
    Terrain.WALL: "contorno",
    Terrain.CRYSTAL: "ceu",
    Terrain.EXIT: "branco",
    Terrain.GATE: "roxo",
}
