"""Amigas que seguem a Bela em fila, pisando onde ela pisou (sem colisao)."""
from src import config
from src.sprites import SPRITE_H, character

T = config.TILE
GAP = 14          # posicoes de distancia entre uma menina e a proxima no rastro


class Trail:
    """Rastro de posicoes da Bela (so grava quando ela anda)."""

    def __init__(self, x, y, size=GAP * 4):
        self.points = [(x, y, (0, 1))] * size

    def push(self, x, y, facing):
        lx, ly, _ = self.points[-1]
        if abs(lx - x) + abs(ly - y) >= 2:
            self.points.append((x, y, facing))
            del self.points[0]

    def reset(self, x, y):
        self.points = [(x, y, (0, 1))] * len(self.points)

    def at(self, k):
        return self.points[max(0, len(self.points) - 1 - k * GAP)]


class Follower:
    def __init__(self, friend, sprite, index):
        self.friend = friend
        self.sprite = sprite
        self.index = index      # 1 = logo atras da Bela
        self.x = self.y = 0.0
        self.facing = (0, 1)
        self.walk = 0
        self.moving = False

    def update(self, trail, leader_moving):
        x, y, facing = trail.at(self.index)
        self.moving = leader_moving and (abs(x - self.x) + abs(y - self.y) > 0.5)
        if self.moving:
            self.walk += 1
        self.x, self.y, self.facing = x, y, facing

    def draw(self, canvas, camera):
        from src.sprites import direction_of
        frames = character(self.sprite)[direction_of(self.facing)]
        frame = frames[1 + (self.walk // 8) % 2] if self.moving else frames[0]
        canvas.blit(frame, (round(self.x) - camera.x, round(self.y) - camera.y + T - SPRITE_H))
