"""O que a Bela leva na jornada: transportes, as amigas que vao junto e as marcas da historia."""
from src import config
from src.transport import ALL, ON_FOOT

FRIEND_NAMES = {"lana": "Lana", "lara": "Lara", "olivia": "Olívia"}
ITEM_NAMES = {"tabuas": "Tábuas", "blocos": "Blocos de montar", "vela": "Pano da vela", "lenha": "Lenha"}


class Inventory:
    def __init__(self):
        self.transports = [ON_FOOT]
        self.friends = []           # amigas que seguem a Bela, na ordem em que entraram
        self.flags = set()          # itens e marcos da historia (ex.: "tabuas", "espinho1")
        if config.DEBUG_UNLOCK_ALL:
            self.transports = list(ALL.values())
            self.friends = list(FRIEND_NAMES)

    def add(self, transport):
        if transport not in self.transports:
            self.transports.append(transport)

    def keep_only(self, keys):
        """Na troca de mapa, so ficam os transportes que fazem sentido no novo lugar."""
        self.transports = [t for t in self.transports if t.key in keys or t is ON_FOOT]

    def join(self, friend):
        if friend not in self.friends:
            self.friends.append(friend)

    def have(self):
        """Tudo o que conta como 'ter' para os pedidos da historia: itens, marcos e amigas."""
        return self.flags | set(self.friends)

    def items(self):
        return [ITEM_NAMES[f] for f in ITEM_NAMES if f in self.flags]
