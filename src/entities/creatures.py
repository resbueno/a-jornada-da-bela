"""Criaturas corrompidas pela Sombra Cinzenta: patrulham o lago e empurram o barco (sem dano)."""
import math

import pygame

from src import config
from src.sprites import flipped, frames

T = config.TILE
P = config.PALETTE


class Eel:
    """Enguia sombria. Se encostar no barco, empurra a Isabela para tras; nao ha dano nem derrota."""

    SPEED = 26.0
    PUSH = 22
    COOLDOWN = 70

    def __init__(self, tile, x_range):
        self.x = tile[0] * T + T / 2
        self.y = tile[1] * T + T / 2
        self.min_x = x_range[0] * T + T / 2
        self.max_x = x_range[1] * T + T / 2
        self.dir = 1
        self.ticks = 0
        self.cooldown = 0

    @property
    def rect(self):
        return pygame.Rect(round(self.x) - 7, round(self.y) - 3, 14, 6)

    def update(self, player, world):
        """Devolve True se empurrou a Isabela neste tick."""
        self.ticks += 1
        self.x += self.dir * self.SPEED * config.DT
        if self.x > self.max_x or self.x < self.min_x:
            self.dir = -self.dir
        if self.cooldown:
            self.cooldown -= 1
            return False
        if player.transport.key != "boat" or player.jumping:
            return False
        hx, hy, hw, hh = player.hitbox
        if not self.rect.colliderect(pygame.Rect(hx, hy, hw, hh)):
            return False
        # empurra para longe da criatura, no eixo de maior diferenca
        dx = (hx + hw / 2) - self.x
        dy = (hy + hh / 2) - self.y
        step = (1 if dx >= 0 else -1, 0) if abs(dx) >= abs(dy) else (0, 1 if dy >= 0 else -1)
        for dist in range(self.PUSH, 0, -2):
            nx, ny = hx + step[0] * dist, hy + step[1] * dist
            if not player._blocked(world, nx, ny):
                player.x += nx - hx
                player.y += ny - hy
                self.cooldown = self.COOLDOWN
                return True
        self.cooldown = self.COOLDOWN
        return False

    def draw(self, canvas, camera):
        sx, sy = round(self.x) - camera.x, round(self.y) - camera.y
        img = frames("eel", 32, 16)[(self.ticks // 7) % 4]
        if self.dir < 0:
            img = flipped(img)
        canvas.blit(img, (sx - 16, sy - 9))


class Minion:
    """Lacaio da Sombra: cruza a estrada de lado a lado. Empurra qualquer transporte, sem dano."""

    SPEED = 34.0
    PUSH = 26
    COOLDOWN = 60

    def __init__(self, tile, y_range):
        self.x = tile[0] * T + T / 2
        self.y = tile[1] * T + T / 2
        self.min_y = y_range[0] * T + T / 2
        self.max_y = y_range[1] * T + T / 2
        self.dir = 1
        self.ticks = 0
        self.cooldown = 0

    @property
    def rect(self):
        return pygame.Rect(round(self.x) - 6, round(self.y) - 8, 12, 16)

    def update(self, player, world):
        self.ticks += 1
        self.y += self.dir * self.SPEED * config.DT
        if self.y > self.max_y or self.y < self.min_y:
            self.dir = -self.dir
        if self.cooldown:
            self.cooldown -= 1
            return False
        if player.jumping:
            return False
        hx, hy, hw, hh = player.hitbox
        if not self.rect.colliderect(pygame.Rect(hx, hy, hw, hh)):
            return False
        dx = (hx + hw / 2) - self.x
        step = (-1, 0) if dx < 0 else (1, 0)
        for dist in range(self.PUSH, 0, -2):          # empurra para tras (para o lado da pista)
            for st in (step, (-step[0], 0)):
                nx, ny = hx + st[0] * dist, hy
                if not player._blocked(world, nx, ny):
                    player.x += nx - hx
                    self.cooldown = self.COOLDOWN
                    return True
        self.cooldown = self.COOLDOWN
        return False

    def draw(self, canvas, camera):
        sx, sy = round(self.x) - camera.x, round(self.y) - camera.y
        sheet = frames("minion_down" if self.dir > 0 else "minion_up", 16, 24)
        canvas.blit(sheet[(self.ticks // 8) % 2], (sx - 8, sy - 16))
