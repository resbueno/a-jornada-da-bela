"""Carrega os sprites (assets/sprites/*.png, quadros lado a lado) e compoe os veiculos com as meninas."""
import pygame

from src.world.tilemap import ROOT

SPRITE_W, SPRITE_H = 32, 48
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


# --- veiculos com a Isabela (e as amigas) montadas --------------------------------------
VEHICLE_SIZE = {"boat": (96, 80), "unicorn": (64, 64)}
# linhas do sprite das meninas que aparecem, y do topo delas, veiculo por cima delas?
RIDER = {
    "boat": (34, 26, True),       # o casco cobre as pernas
    "unicorn": (34, 8, False),    # as meninas por cima do corpo do unicornio
}
# lugar (x) da Isabela e das amigas em cada vista; vista de lado olhando para a esquerda
SEATS = {
    "boat": {"side": [36, 50, 62], "front": [32, 18, 46], "back": [32, 18, 46]},
    "unicorn": {"side": [14, 26], "front": [16, 16], "back": [16, 16]},
}
_veh_cache = {}


def _load_vehicle(key, view):
    w, h = VEHICLE_SIZE[key]
    sheet = pygame.image.load(str(ROOT / "assets" / "sprites" / f"vehicle_{key}_{view}.png")).convert_alpha()
    return [sheet.subsurface((i * w, 0, w, h)).copy() for i in range(sheet.get_width() // w)]


def vehicle_frame(key, facing, frame, rider_name="isabela", passengers=()):
    """Veiculo com a cavaleira e as amigas ja compostos. `frame` 0/1."""
    direction = direction_of(facing)
    ck = (key, direction, frame % 2, rider_name, tuple(passengers))
    if ck in _veh_cache:
        return _veh_cache[ck]
    view = {"down": "front", "up": "back", "left": "side", "right": "side"}[direction]
    w, h = VEHICLE_SIZE[key]
    frames = _load_vehicle(key, view)
    veh = frames[frame % len(frames)]
    rows, top, veh_over = RIDER[key]
    seats = SEATS[key][view]
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    if not veh_over:
        out.blit(veh if direction != "right" else pygame.transform.flip(veh, True, False), (0, 0))
    riders = [rider_name] + list(passengers)
    order = list(range(len(riders)))[::-1]          # as de tras primeiro; a Isabela por ultimo
    for i in order:
        if i >= len(seats):
            continue
        body = character(riders[i])[direction][0].subsurface((0, 0, SPRITE_W, rows))
        x = seats[i]
        if direction == "right":
            x = w - x - SPRITE_W
        lift = 0 if i == 0 or view == "side" else 6  # nas vistas de frente/costas, as amigas aparecem atras
        out.blit(body, (x, top - lift - (2 if i and view == "side" else 0)))
    if veh_over:
        out.blit(veh if direction != "right" else pygame.transform.flip(veh, True, False), (0, 0))
    _veh_cache[ck] = out
    return out


# --- folhas de sprites genericas (bichos, objetos) -------------------------------------------
_sheet_cache = {}


def frames(name, fw, fh=None):
    """Quadros fw x fh de assets/sprites/<name>.png (lado a lado), em cache. Sem fh: altura da folha."""
    key = (name, fw, fh)
    if key not in _sheet_cache:
        sheet = pygame.image.load(str(ROOT / "assets" / "sprites" / f"{name}.png")).convert_alpha()
        h = fh or sheet.get_height()
        _sheet_cache[key] = [sheet.subsurface((i * fw, 0, fw, h)).copy() for i in range(sheet.get_width() // fw)]
    return _sheet_cache[key]


_flip_cache = {}


def flipped(surface):
    """Espelho horizontal em cache (os sprites dos bichos olham para a esquerda)."""
    k = id(surface)
    if k not in _flip_cache:
        _flip_cache[k] = (surface, pygame.transform.flip(surface, True, False))
    return _flip_cache[k][1]
