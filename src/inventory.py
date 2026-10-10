"""Transportes que a Bela possui. Comeca so com 'a pe'; NPCs entregam os demais (componente 7)."""
from src import config
from src.transport import ALL, ON_FOOT


class Inventory:
    def __init__(self):
        self.transports = [ON_FOOT]
        self.insumos = set()        # insumos que nao sao transportes (ex.: "dragon")
        self.flags = set()          # itens e marcos da historia (ex.: "oar")
        if config.DEBUG_UNLOCK_ALL_TRANSPORTS:
            self.transports = list(ALL.values())

    def add(self, transport):
        if transport not in self.transports:
            self.transports.append(transport)

    def has(self, transport):
        return transport in self.transports

    REQUIRED = ("boat", "unicorn", "pink_car", "dragon")

    def count_insumos(self):
        keys = {t.key for t in self.transports} | self.insumos
        return sum(1 for k in self.REQUIRED if k in keys)

    def has_all_insumos(self):
        return self.count_insumos() == len(self.REQUIRED)
