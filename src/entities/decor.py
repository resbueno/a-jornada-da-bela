"""Decorativos: aves, animais, peixes e arco-iris. Reagem a Bela so visualmente.

Nao tem colisao e nao afetam a progressao. Contam ticks (passo fixo), sem aleatoriedade.
"""
import math

import pygame

from src import config

T = config.TILE
P = config.PALETTE


def _dist(ax, ay, bx, by):
    return math.hypot(ax - bx, ay - by)


def _away(px, py, qx, qy):
    """Vetor unitario que vai de (qx, qy) para longe de (px, py)."""
    dx, dy = qx - px, qy - py
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


class Decor:
    def __init__(self, tile, phase=0):
        self.home = (tile[0] * T + T / 2, tile[1] * T + T / 2)  # centro do tile
        self.x, self.y = self.home
        self.ticks = phase
        self.layer = "ground"  # "back" (atras de tudo), "ground" ou "air"

    def update(self, player_center):
        self.ticks += 1

    def draw(self, canvas, camera):
        pass

    def _screen(self, camera):
        return round(self.x) - camera.x, round(self.y) - camera.y


class Bird(Decor):
    NEAR, FAR, SPEED, FLEE_TICKS = 36, 120, 110.0, 90

    def __init__(self, tile, phase=0):
        super().__init__(tile, phase)
        self.layer = "air"
        self.state = "idle"
        self.flee_left = 0
        self.vx = self.vy = 0.0

    def update(self, pc):
        super().update(pc)
        d = _dist(pc[0], pc[1], self.x, self.y)
        if self.state == "idle" and d < self.NEAR:
            ax, ay = _away(pc[0], pc[1], self.x, self.y)
            self.vx, self.vy = ax, ay - 0.6
            n = math.hypot(self.vx, self.vy) or 1.0
            self.vx, self.vy = self.vx / n, self.vy / n
            self.state, self.flee_left = "flee", self.FLEE_TICKS
        elif self.state == "flee":
            self.x += self.vx * self.SPEED * config.DT
            self.y += self.vy * self.SPEED * config.DT
            self.flee_left -= 1
            if self.flee_left <= 0:
                self.state = "gone"
        elif self.state == "gone":
            if _dist(pc[0], pc[1], *self.home) > self.FAR:
                self.state = "idle"
                self.x, self.y = self.home

    def draw(self, canvas, camera):
        if self.state == "gone":
            return
        sx, sy = self._screen(camera)
        flap = (self.ticks // (4 if self.state == "flee" else 40)) % 2
        pygame.draw.rect(canvas, P["amarelo_brilho"], (sx - 2, sy - 1, 5, 3))
        pygame.draw.rect(canvas, P["contorno"], (sx + 2, sy - 1, 1, 1))  # olho
        wing_y = sy - 3 if flap else sy + 1
        pygame.draw.rect(canvas, P["creme"], (sx - 1, wing_y, 3, 1))


class Animal(Decor):
    NEAR, FAR, RUN, BACK, DIST = 44, 80, 90.0, 40.0, 40.0

    def __init__(self, tile, phase=0):
        super().__init__(tile, phase)
        self.state = "idle"
        self.target = self.home

    def update(self, pc):
        super().update(pc)
        d = _dist(pc[0], pc[1], self.x, self.y)
        if self.state == "idle" and d < self.NEAR:
            ax, ay = _away(pc[0], pc[1], self.x, self.y)
            self.target = (self.home[0] + ax * self.DIST, self.home[1] + ay * self.DIST)
            self.state = "run"
        elif self.state == "run":
            if self._step_to(self.target, self.RUN):
                self.state = "wait"
        elif self.state == "wait":
            if _dist(pc[0], pc[1], *self.home) > self.FAR:
                self.state = "back"
        elif self.state == "back":
            if self._step_to(self.home, self.BACK):
                self.state = "idle"

    def _step_to(self, target, speed):
        dx, dy = target[0] - self.x, target[1] - self.y
        n = math.hypot(dx, dy)
        step = speed * config.DT
        if n <= step:
            self.x, self.y = target
            return True
        self.x += dx / n * step
        self.y += dy / n * step
        return False

    def draw(self, canvas, camera):
        sx, sy = self._screen(camera)
        hop = -1 if (self.ticks // (6 if self.state == "run" else 40)) % 2 else 0
        pygame.draw.rect(canvas, P["creme"], (sx - 4, sy - 2 + hop, 8, 5))      # corpo
        pygame.draw.rect(canvas, P["creme"], (sx + 2, sy - 5 + hop, 3, 4))      # cabeca
        pygame.draw.rect(canvas, P["rosa"], (sx + 3, sy - 7 + hop, 1, 2))       # orelha
        pygame.draw.rect(canvas, P["contorno"], (sx + 4, sy - 4 + hop, 1, 1))   # olho


class Fish(Decor):
    NEAR, IDLE_PERIOD, NEAR_PERIOD, JUMP = 56, 180, 60, 24

    def __init__(self, tile, phase=0):
        super().__init__(tile, phase)
        self.layer = "ground"
        self.since = phase % self.IDLE_PERIOD
        self.jump_t = -1
        self.near = False

    def update(self, pc):
        super().update(pc)
        self.near = _dist(pc[0], pc[1], *self.home) < self.NEAR
        if self.jump_t >= 0:
            self.jump_t += 1
            if self.jump_t >= self.JUMP:
                self.jump_t = -1
                self.since = 0
            return
        self.since += 1
        if self.since >= (self.NEAR_PERIOD if self.near else self.IDLE_PERIOD):
            self.jump_t = 0

    def draw(self, canvas, camera):
        sx, sy = self._screen(camera)
        if self.jump_t < 0:
            if (self.ticks // 30) % 2:
                pygame.draw.rect(canvas, P["ceu_reflexo"], (sx - 2, sy, 4, 1))  # ondinha
            return
        h = round(7 * math.sin(math.pi * self.jump_t / self.JUMP))
        pygame.draw.rect(canvas, P["creme"], (sx - 2, sy - h, 4, 2))
        pygame.draw.rect(canvas, P["ceu_reflexo"], (sx - 3, sy, 6, 1))        # respingo


class Rainbow(Decor):
    NEAR = 64
    BANDS = ("rosa", "amarelo_brilho", "ceu_reflexo", "lilas_magia")
    OUTER, BAND_W = 24, 3
    _cache = {}

    def __init__(self, tile, phase=0):
        super().__init__(tile, phase)
        self.layer = "back"
        self.near = False

    @classmethod
    def _surface(cls, shift):
        """Arco desenhado coluna a coluna (limpo em pixel art), um por deslocamento de cor."""
        if shift in cls._cache:
            return cls._cache[shift]
        R, W = cls.OUTER, cls.BAND_W
        surf = pygame.Surface((R * 2, R), pygame.SRCALPHA)
        for dx in range(-R, R):
            cx = dx + 0.5
            for i in range(len(cls.BANDS)):
                r_out, r_in = R - i * W, R - (i + 1) * W
                if abs(cx) >= r_out:
                    continue
                top = R - math.floor(math.sqrt(r_out * r_out - cx * cx))
                bottom = R - (math.floor(math.sqrt(r_in * r_in - cx * cx)) if abs(cx) < r_in else 0)
                color = P[cls.BANDS[(i + shift) % len(cls.BANDS)]]
                if bottom > top:
                    pygame.draw.rect(surf, color, (dx + R, top, 1, bottom - top))
        cls._cache[shift] = surf
        return surf

    def update(self, pc):
        super().update(pc)
        self.near = _dist(pc[0], pc[1], *self.home) < self.NEAR

    def draw(self, canvas, camera):
        sx, sy = self._screen(camera)
        shift = (self.ticks // 8) % len(self.BANDS) if self.near else 0
        canvas.blit(self._surface(shift), (sx - self.OUTER, sy - self.OUTER))


KINDS = {"bird": Bird, "animal": Animal, "fish": Fish, "rainbow": Rainbow}
