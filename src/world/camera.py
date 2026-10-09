"""Camera de scroll suave: segue o alvo, presa as bordas do mapa, sempre em pixels inteiros."""
from src import config


class Camera:
    def __init__(self, world_w, world_h):
        self.world_w = world_w
        self.world_h = world_h
        self.x = 0
        self.y = 0

    def follow(self, cx, cy):
        """Centraliza em (cx, cy) em coordenadas do mundo."""
        self.x = self._axis(cx, config.LOGICAL_W, self.world_w)
        self.y = self._axis(cy, config.LOGICAL_H, self.world_h)

    @staticmethod
    def _axis(center, view, world):
        if world <= view:  # mapa menor que a tela: centraliza
            return -((view - world) // 2)
        return round(min(max(center - view / 2, 0), world - view))
