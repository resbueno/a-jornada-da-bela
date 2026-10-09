"""Transportes que a Bela possui. Comeca so com 'a pe'; NPCs entregam os demais (componente 7)."""
from src import config
from src.transport import ALL, ON_FOOT


class Inventory:
    def __init__(self):
        self.transports = [ON_FOOT]
        if config.DEBUG_UNLOCK_ALL_TRANSPORTS:
            self.transports = list(ALL.values())

    def add(self, transport):
        if transport not in self.transports:
            self.transports.append(transport)

    def has(self, transport):
        return transport in self.transports
