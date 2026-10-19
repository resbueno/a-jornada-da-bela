"""A Bela: posicao em float, hitbox pequena nos pes, colisao por terreno do tile."""
import math

import pygame

from src import config
from src.sprites import SPRITE_H, VEHICLE_SIZE, character, direction_of, vehicle_frame
from src.transport import ON_FOOT
from src.world.terrain import Terrain

T = config.TILE
EPS = 1e-6


class Player:
    # Hitbox nos pes, em relacao ao canto superior esquerdo do tile 32x32
    HIT_W = 20
    HIT_H = 12
    HIT_OX = 6
    HIT_OY = 20

    def __init__(self, x, y, transport=ON_FOOT):
        self.x = float(x)
        self.y = float(y)
        self.transport = transport
        self.facing = (0, 1)  # para baixo
        self.moving = False
        self.walk_ticks = 0
        self.sprite_name = "isabela"
        self.passengers = ()        # amigas montadas junto (unicornio, barco)
        self.jump_t = -1            # -1: no chao; 0..JUMP_TICKS: no ar
        self.trail = []             # particulas: [x, y, vida, vida_max]
        self._jump_from = (0.0, 0.0)
        self._jump_to = (0.0, 0.0)

    # --- hitbox ------------------------------------------------------
    @property
    def hitbox(self):
        return (self.x + self.HIT_OX, self.y + self.HIT_OY, self.HIT_W, self.HIT_H)

    @property
    def center(self):
        return (self.x + T / 2, self.y + T / 2)

    @property
    def feet(self):
        hx, hy, hw, hh = self.hitbox
        return (hx + hw / 2, hy + hh / 2)

    def _blocked(self, world, hx, hy, transport=None):
        transport = transport or self.transport
        left = math.floor(hx / T)
        right = math.floor((hx + self.HIT_W - EPS) / T)
        top = math.floor(hy / T)
        bottom = math.floor((hy + self.HIT_H - EPS) / T)
        for ty in range(top, bottom + 1):
            for tx in range(left, right + 1):
                if (tx, ty) in world.solid_tiles:
                    return True
                if not transport.can_enter(world.terrain_at(tx, ty)):
                    return True
        return False

    def facing_tiles(self):
        """Tiles logo a frente da Bela (para interagir), do mais perto ao mais longe."""
        cx, cy = self.feet
        fx, fy = self.facing
        return [(int((cx + fx * d) // T), int((cy + fy * d) // T)) for d in (16, 28, 44)]

    # --- salto (unicornio) -------------------------------------------
    JUMP_TICKS = 28
    JUMP_HEIGHT = 26

    @property
    def jumping(self):
        return self.jump_t >= 0

    def try_jump(self, world):
        """Unicornio salta um desfiladeiro de 1 ou 2 tiles a frente. True se saltou."""
        if self.transport.key != "unicorn" or self.jumping:
            return False
        fx, fy = self.facing
        hx, hy, hw, hh = self.hitbox
        cx, cy = hx + hw / 2, hy + hh / 2
        tx, ty = int(cx // T), int(cy // T)

        def kind(k):
            return world.terrain_at(tx + fx * k, ty + fy * k)

        if kind(1) is not Terrain.FISSURE:
            return False
        land = 2 if kind(2) is not Terrain.FISSURE else 3
        if land == 3 and kind(3) is Terrain.FISSURE:
            return False
        ltx, lty = tx + fx * land, ty + fy * land
        new_cx = ltx * T + T / 2 if fx else cx
        new_cy = lty * T + T / 2 if fy else cy
        nhx, nhy = new_cx - hw / 2, new_cy - hh / 2
        if self._blocked(world, nhx, nhy):
            return False
        self._jump_from = (self.x, self.y)
        self._jump_to = (self.x + (nhx - hx), self.y + (nhy - hy))
        self.jump_t = 0
        return True

    def update_jump(self):
        """Avanca o salto 1 tick. Devolve True enquanto estiver no ar."""
        if not self.jumping:
            return False
        self.jump_t += 1
        u = min(self.jump_t / self.JUMP_TICKS, 1.0)
        self.x = self._jump_from[0] + (self._jump_to[0] - self._jump_from[0]) * u
        self.y = self._jump_from[1] + (self._jump_to[1] - self._jump_from[1]) * u
        if self.jump_t >= self.JUMP_TICKS:
            self.jump_t = -1
            self.x, self.y = self._jump_to
            return False
        return True

    def can_use(self, transport, world):
        """True se a hitbox atual so toca terrenos que `transport` pode pisar."""
        hx, hy, _, _ = self.hitbox
        return not self._blocked(world, hx, hy, transport)

    SWITCH_REACH = 40  # px: distancia maxima ate o terreno compativel (margem)

    def switch_transport(self, transport, world):
        """Troca de transporte. Se o terreno sob a Bela nao serve, mas ha terreno
        compativel a ate SWITCH_REACH px (margem), ela e movida para la.
        Devolve True se trocou."""
        if self.can_use(transport, world):
            self.transport = transport
            return True
        hx, hy, _, _ = self.hitbox
        dirs = [self.facing] + [d for d in ((1, 0), (-1, 0), (0, 1), (0, -1)) if d != self.facing]
        for dist in range(2, self.SWITCH_REACH + 1, 2):
            for dx, dy in dirs:
                nx, ny = hx + dx * dist, hy + dy * dist
                if not self._blocked(world, nx, ny, transport):
                    self.x += nx - hx
                    self.y += ny - hy
                    self.transport = transport
                    return True
        return False

    # --- movimento ---------------------------------------------------
    def move(self, dx, dy, dt, world):
        """Anda (dx, dy) em {-1,0,1} com colisao por eixo; encosta na borda do tile ao bater.
        Devolve True se bateu em algo."""
        self.moving = bool(dx or dy)
        if self.moving:
            self.facing = (dx, dy)
            self.walk_ticks += 1
        else:
            self.walk_ticks = 0
        self._emit_trail(dx, dy)
        return self._slide(dx, dy, self.transport.speed * dt, world)

    def drift(self, dx, dy, speed, dt, world):
        """Empurrao do ambiente (correnteza, vento): mexe sem virar o rosto. True se bateu."""
        return self._slide(dx, dy, speed * dt, world)

    def _slide(self, dx, dy, step, world):
        hx, hy, _, _ = self.hitbox
        hit = False
        if dx:
            nx = hx + dx * step
            if self._blocked(world, nx, hy):
                hit = True
                if dx > 0:
                    nx = math.floor((nx + self.HIT_W) / T) * T - self.HIT_W
                else:
                    nx = (math.floor(nx / T) + 1) * T
                nx = nx if (nx - hx) * dx > 0 else hx  # nunca recua nem anda alem do passo
            self.x += nx - hx
            hx = nx
        if dy:
            ny = hy + dy * step
            if self._blocked(world, hx, ny):
                hit = True
                if dy > 0:
                    ny = math.floor((ny + self.HIT_H) / T) * T - self.HIT_H
                else:
                    ny = (math.floor(ny / T) + 1) * T
                ny = ny if (ny - hy) * dy > 0 else hy
            self.y += ny - hy
        return hit

    def _emit_trail(self, dx, dy):
        """Espuma atras do barco e brilhinhos atras do unicornio (so enquanto anda)."""
        for p in self.trail:
            p[2] -= 1
        self.trail = [p for p in self.trail if p[2] > 0]
        key = self.transport.key
        if (dx or dy) and key in ("boat", "unicorn") and self.walk_ticks % 3 == 0:
            hx, hy, hw, hh = self.hitbox
            self.trail.append([hx + hw / 2 - dx * 20, hy + hh - dy * 14, 22, 22])

    # --- desenho -----------------------------------------------------
    def draw(self, canvas, camera):
        sx = round(self.x) - camera.x
        sy = round(self.y) - camera.y
        if self.jumping:
            sy -= round(self.JUMP_HEIGHT * math.sin(math.pi * self.jump_t / self.JUMP_TICKS))
        step = (self.walk_ticks // 8) % 2 if (self.moving or self.jumping) else 0
        for x, y, life, life_max in self.trail:                   # rastro (atras do veiculo)
            u = life / life_max
            size = 2 + int((1 - u) * 6)
            color = config.PALETTE["branco" if self.transport.key == "boat" else "rosa"]
            canvas.fill(color, (round(x) - camera.x, round(y) - camera.y - int((1 - u) * 8), size, size))
        if self.transport.key != "on_foot":
            vw, vh = VEHICLE_SIZE[self.transport.key]
            surf = vehicle_frame(self.transport.key, self.facing, step, self.sprite_name, self.passengers)
            canvas.blit(surf, (sx - (vw - T) // 2, sy + T - vh + (10 if self.transport.key == "boat" else 0)))
        else:
            frames = character(self.sprite_name)[direction_of(self.facing)]
            frame = frames[1 + step] if self.moving else frames[0]
            canvas.blit(frame, (sx, sy + T - SPRITE_H))
        if config.DEBUG_HITBOX:
            hx, hy, hw, hh = self.hitbox
            pygame.draw.rect(canvas, config.PALETTE["vermelho"],
                             (round(hx) - camera.x, round(hy) - camera.y, hw, hh), 2)
