"""Carrega os sprites de personagem (assets/sprites/<nome>_<direcao>.png, 3 frames lado a lado)."""
import pygame

from src.world.tilemap import ROOT

SPRITE_W, SPRITE_H = 16, 24
_cache = {}


def _load_dir(name, direction):
    sheet = pygame.image.load(str(ROOT / "assets" / "sprites" / f"{name}_{direction}.png")).convert_alpha()
    return [sheet.subsurface((i * SPRITE_W, 0, SPRITE_W, SPRITE_H)).copy() for i in range(sheet.get_width() // SPRITE_W)]


def character(name):
    """Devolve {'down'|'up'|'left'|'right': [frame0, frame1, frame2]} (right = espelho de left)."""
    if name not in _cache:
        left = _load_dir(name, "left")
        _cache[name] = {
            "down": _load_dir(name, "down"),
            "up": _load_dir(name, "up"),
            "left": left,
            "right": [pygame.transform.flip(f, True, False) for f in left],
        }
    return _cache[name]


def direction_of(facing):
    fx, fy = facing
    if fy > 0:
        return "down"
    if fy < 0:
        return "up"
    return "left" if fx < 0 else "right"


# --- veiculos (32x32) com a Isabela montada ----------------------------------------
VEHICLE_W = VEHICLE_H = 32
# (linhas do sprite da Isabela mantidas, y do topo do cavaleiro, vehicle_em_cima_do_cavaleiro)
RIDER = {
    "boat": (17, 6, True),       # casco cobre as pernas
    "unicorn": (17, 4, False),   # cavaleiro por cima do corpo do unicornio
    "pink_car": (13, 10, True),  # carroceria cobre o corpo dela
}
_veh_cache = {}


def _load_vehicle(key, view):
    sheet = pygame.image.load(str(ROOT / "assets" / "sprites" / f"vehicle_{key}_{view}.png")).convert_alpha()
    return [sheet.subsurface((i * VEHICLE_W, 0, VEHICLE_W, VEHICLE_H)).copy()
            for i in range(sheet.get_width() // VEHICLE_W)]


def vehicle_frame(key, facing, frame, rider_name="isabela"):
    """Veiculo + cavaleira ja compostos (32x32). `frame` 0/1."""
    direction = direction_of(facing)
    ck = (key, direction, frame % 2, rider_name)
    if ck in _veh_cache:
        return _veh_cache[ck]
    view = {"down": "front", "up": "back", "left": "side", "right": "side"}[direction]
    frames = _load_vehicle(key, view)
    veh = frames[frame % len(frames)]
    if direction == "right":
        veh = pygame.transform.flip(veh, True, False)
    rows, top, veh_over = RIDER[key]
    rider_full = character(rider_name)[direction][0]
    rider = rider_full.subsurface((0, 0, SPRITE_W, rows)).copy()
    out = pygame.Surface((VEHICLE_W, VEHICLE_H), pygame.SRCALPHA)
    x = (VEHICLE_W - SPRITE_W) // 2
    if veh_over:
        out.blit(rider, (x, top))
        out.blit(veh, (0, 0))
    else:
        out.blit(veh, (0, 0))
        out.blit(rider, (x, top))
    _veh_cache[ck] = out
    return out
