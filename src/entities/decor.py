"""Decorativos: aves, animais, peixes e arco-iris. Reagem a Bela so visualmente.

Nao tem colisao e nao afetam a progressao. Contam ticks (passo fixo), sem aleatoriedade.
"""
import math

import pygame

from src import config
from src.sprites import flipped, frames

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
    VARIANTS = ("bird_yellow", "bird_blue", "bird_red")

    def __init__(self, tile, phase=0):
        super().__init__(tile, phase)
        self.layer = "air"
        self.state = "idle"
        self.flee_left = 0
        self.vx = self.vy = 0.0
        self.variant = self.VARIANTS[(tile[0] * 7 + tile[1] * 3) % 3]
        self.face_right = (tile[0] + tile[1]) % 2 == 0

    def update(self, pc):
        super().update(pc)
        d = _dist(pc[0], pc[1], self.x, self.y)
        if self.state == "idle" and d < self.NEAR:
            ax, ay = _away(pc[0], pc[1], self.x, self.y)
            self.vx, self.vy = ax, ay - 0.6
            n = math.hypot(self.vx, self.vy) or 1.0
            self.vx, self.vy = self.vx / n, self.vy / n
            self.face_right = self.vx > 0
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
        sheet = frames(self.variant, 16, 16)
        if self.state == "flee":
            img = sheet[2 + (self.ticks // 4) % 2]
        else:                                   # pousado: de vez em quando inclina a cabeca
            img = sheet[1 if (self.ticks // 35) % 5 == 4 else 0]
        if self.face_right:
            img = flipped(img)
        canvas.blit(img, (sx - 8, sy - 11))


class Animal(Decor):
    """Coelho: senta, mexe a orelha, e foge em pulos quando a Bela chega perto."""
    NEAR, FAR, RUN, BACK, DIST = 44, 80, 90.0, 40.0, 40.0
    VARIANTS = ("rabbit_white", "rabbit_brown", "rabbit_gray")

    def __init__(self, tile, phase=0):
        super().__init__(tile, phase)
        self.state = "idle"
        self.target = self.home
        self.variant = self.VARIANTS[(tile[0] * 5 + tile[1] * 11) % 3]
        self.face_right = (tile[0] * 3 + tile[1]) % 2 == 0

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
        if abs(dx) > 0.3:
            self.face_right = dx > 0
        if n <= step:
            self.x, self.y = target
            return True
        self.x += dx / n * step
        self.y += dy / n * step
        return False

    def draw(self, canvas, camera):
        sx, sy = self._screen(camera)
        sheet = frames(self.variant, 16, 16)
        bounce = 0
        if self.state == "run":                       # pulos: agachado / no ar
            air = (self.ticks // 6) % 2
            img = sheet[3 if air else 2]
            bounce = -4 if air else 0
        elif self.state == "back":                    # volta aos pulinhos
            air = (self.ticks // 14) % 2
            img = sheet[3 if air else 2]
            bounce = -2 if air else 0
        else:                                         # sentado, mexendo a orelha de vez em quando
            img = sheet[1 if (self.ticks // 30) % 6 == 5 else 0]
        if self.face_right:
            img = flipped(img)
        canvas.blit(img, (sx - 8, sy - 13 + bounce))


class Fish(Decor):
    NEAR, IDLE_PERIOD, NEAR_PERIOD, JUMP = 56, 180, 60, 24
    VARIANTS = ("fish_orange", "fish_blue")

    def __init__(self, tile, phase=0):
        super().__init__(tile, phase)
        self.layer = "ground"
        self.since = phase % self.IDLE_PERIOD
        self.jump_t = -1
        self.near = False
        self.variant = self.VARIANTS[(tile[0] + tile[1]) % 2]
        self.face_right = (tile[0] * 2 + tile[1]) % 2 == 0

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
                pygame.draw.rect(canvas, P["ceu_reflexo"], (sx - 3, sy, 6, 1))     # ondinha
                canvas.set_at((sx - 1, sy - 1), P["branco"])
            return
        u = self.jump_t / self.JUMP
        h = round(9 * math.sin(math.pi * u))
        sheet = frames(self.variant, 16, 16)
        img = sheet[1] if u < 0.34 else (sheet[2] if u < 0.66 else sheet[3])
        if self.face_right:
            img = flipped(img)
        canvas.blit(img, (sx - 8, sy - 8 - h))
        if u < 0.2 or u > 0.8:                                                    # respingo
            pygame.draw.rect(canvas, P["ceu_reflexo"], (sx - 5, sy, 10, 1))
            canvas.set_at((sx - 6, sy - 1), P["branco"]); canvas.set_at((sx + 5, sy - 1), P["branco"])


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
