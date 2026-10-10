"""Criaturas corrompidas pela Sombra Cinzenta: patrulham o lago e empurram o barco (sem dano)."""
import math

import pygame

from src import config

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
        wave = int(math.sin(self.ticks / 8.0) * 1.5)
        flip = self.dir < 0
        # corpo em S
        for i in range(-6, 7):
            yy = sy + int(math.sin((i + self.ticks / 5.0) / 2.2) * 1.6)
            xx = sx + i
            color = P["roxo"] if abs(i) < 5 else P["azul"]
            canvas.set_at((xx, yy), color)
            canvas.set_at((xx, yy + 1), P["contorno"] if i % 3 else P["azul"])
        head = sx - 7 if flip else sx + 7
        canvas.set_at((head, sy + wave), P["roxo"])
        canvas.set_at((head - (1 if not flip else -1), sy + wave), P["vermelho"])  # olho


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
        step = (self.ticks // 8) % 2
        body = [(-4, -2, 8, 8, "roxo"), (-3, -8, 6, 6, "contorno"), (-5, 6, 4, 3, "azul"), (1, 6, 4, 3, "azul")]
        for dx, dy, w, h, c in body:
            pygame.draw.rect(canvas, P[c], (sx + dx, sy + dy + (1 if step and dy == 6 else 0), w, h))
        pygame.draw.rect(canvas, P["vermelho"], (sx - 2, sy - 6, 1, 1))     # olhos
        pygame.draw.rect(canvas, P["vermelho"], (sx + 1, sy - 6, 1, 1))
        pygame.draw.rect(canvas, P["rosa_escuro"], (sx - 7, sy - 1, 3, 2))  # braco com lanca
        pygame.draw.rect(canvas, P["areia_clara"], (sx - 7, sy - 9, 1, 10))
