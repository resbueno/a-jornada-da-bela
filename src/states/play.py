"""Estado Jogando: mapa, camera, a Bela e as amigas, objetos, tarefas e interface."""
import math

import pygame

from src import config
from src.entities.follower import Follower, Trail
from src.entities.player import Player
from src.input import Action
from src.inventory import Inventory
from src.lighting import FOG, Darkness, Tint
from src.maps import MAPS, sprite_for
from src.states.base import State
from src.states.dialogue import DialogueState
from src.states.inventory import InventoryState
from src.states.pause import Pause
from src.text import draw_text, wrap
from src.transport import ALL, BOAT, ON_FOOT
from src.ui import draw_panel
from src.weather import Rain, Wind
from src.world.camera import Camera
from src.world.objects import load_decor, load_objects
from src.world.terrain import WATERS, Terrain
from src.world.tilemap import Tilemap

T = config.TILE
P = config.PALETTE
W, H = config.LOGICAL_W, config.LOGICAL_H
CARD_TICKS = 170
RAPIDS_SPEED = 90.0      # px/s: correnteza rio abaixo
WIND_SPEED = 170.0       # px/s: mais forte que o passo da Bela, que nao consegue subir


class Play(State):
    def __init__(self, map_id="bosque", inventory=None, spawn=None):
        super().__init__()
        spec = MAPS[map_id]
        self.spec = spec
        self.map_id = map_id
        base = spec["base"]
        self.world = Tilemap.load(base + ".map.txt")
        self.world.style = spec["style"]
        self.objects = load_objects(base + ".objects.json")
        self.decor = load_decor(base + ".decor.json")
        for obj in self.objects:
            if obj.solid:
                self.world.solid_tiles.update(obj.footprint())
        self.inventory = inventory or Inventory()
        self.inventory.keep_only(spec["transports"])
        self.camera = Camera(self.world.pixel_w, self.world.pixel_h)
        sx, sy = spawn or spec["spawn"]
        self.player = Player(sx * T, sy * T)
        self.player.sprite_name = sprite_for("isabela", map_id)
        self.trail = Trail(self.player.x, self.player.y)
        self.followers = []
        self._build_followers()
        self.ticks = 0
        self.toast = ""
        self.toast_ticks = 0
        self.bump_cooldown = 0
        self.wind_note = 0
        on = config.WEATHER != "none"
        self.rain = Rain() if spec.get("weather") == "rain" and on else None
        self.wind = Wind() if spec.get("weather") == "wind" and on else None
        self.darkness = Darkness() if spec.get("dark") else None
        self.fog = Darkness(alpha=150, color=FOG) if spec.get("fog") and on else None
        self.fog_amount = 0.0
        self.tint = Tint(spec["tint"]) if spec.get("tint") else None
        self.intro_pending = list(spec.get("intro", []))
        self.lamps = [(x, y) for y in range(self.world.rows) for x in range(self.world.cols)
                      if self.world.grid[y][x] is Terrain.LAMP]
        self.camera.follow(*self.player.center)

    # ------------------------------------------------------------ amigas
    def _build_followers(self):
        self.followers = [Follower(f, sprite_for(f, self.map_id), i + 1)
                          for i, f in enumerate(self.inventory.friends)]
        for f in self.followers:
            f.x, f.y = self.player.x, self.player.y

    def _say(self, speaker, lines, on_finish=None):
        self.manager.push(DialogueState(speaker, lines, on_finish))

    def _toast(self, text, ticks=150):
        self.toast, self.toast_ticks = text, ticks

    # ------------------------------------------------------------ ciclo
    def update(self, dt, inp):
        self.ticks += 1
        if self.rain:
            self.rain.update()
        if self.wind:
            self.wind.update()
        if self.intro_pending and self.ticks == 70:
            lines, self.intro_pending = self.intro_pending, []
            self._say("", lines)
            return
        if inp.pressed(Action.PAUSE):
            self.manager.push(Pause(self))
            return
        if inp.pressed(Action.INVENTORY):
            self.manager.push(InventoryState(self))
            return
        if self.toast_ticks:
            self.toast_ticks -= 1
        if self.bump_cooldown:
            self.bump_cooldown -= 1
        pl = self.player
        if inp.pressed(Action.INTERACT) and not pl.jumping:
            target = self._interactable_in_front()
            if target:
                self._talk(target)
                return
            if not pl.try_jump(self.world) and self._facing_terrain() is Terrain.FISSURE:
                self._toast("É fundo demais! Só pulando com o unicórnio." if pl.transport.key != "unicorn"
                            else "Chegue mais perto da beirada para pular.")
        if pl.jumping:
            pl.update_jump()
        else:
            dx, dy = inp.direction()
            self._auto_board(dx, dy)
            pl.move(dx, dy, dt, self.world)
            self._environment(dt)
        self.camera.follow(*pl.center)
        riding = pl.transport is not ON_FOOT
        pl.passengers = tuple(f.sprite for f in self.followers) if riding else ()
        self.trail.push(pl.x, pl.y, pl.facing)
        for f in self.followers:
            f.update(self.trail, pl.moving or pl.jumping)
        for d in self.decor:
            d.update(pl.center)
        on_water = pl.transport is BOAT
        if self.rain:
            self.rain.heavy = on_water
        target = 1.0 if on_water else 0.0
        self.fog_amount += (target - self.fog_amount) * 0.03
        self._check_exit()

    def _facing_terrain(self):
        tx, ty = self.player.facing_tiles()[0]
        return self.world.terrain_at(tx, ty)

    def _auto_board(self, dx, dy):
        """Com o barco: entrar na agua embarca; encostar na terra (cais) desembarca."""
        pl = self.player
        if not (dx or dy):
            return
        hx, hy, hw, hh = pl.hitbox
        cx, cy = hx + hw / 2 + dx * (hw / 2 + 6), hy + hh / 2 + dy * (hh / 2 + 6)
        ahead = self.world.terrain_at(int(cx // T), int(cy // T))
        if pl.transport is ON_FOOT and ahead in WATERS and BOAT in self.inventory.transports:
            pl.facing = (dx, dy)
            if pl.switch_transport(BOAT, self.world):
                self.trail.reset(pl.x, pl.y)
                if "a_bordo" not in self.inventory.flags:
                    self.inventory.flags.add("a_bordo")
                    self._toast("Lana amarrou as velas e Bela acendeu a lanterna. Rio abaixo!", 220)
        elif pl.transport is BOAT and ahead in ON_FOOT.terrains and (int(cx // T), int(cy // T)) not in self.world.solid_tiles:
            pl.facing = (dx, dy)
            if pl.switch_transport(ON_FOOT, self.world):
                self.trail.reset(pl.x, pl.y)

    def _environment(self, dt):
        """Correnteza empurra o barco rio abaixo; o vento empurra quem tenta subir a trilha."""
        pl = self.player
        here = self.world.terrain_at_pixel(*pl.feet)
        if here is Terrain.RAPIDS and pl.transport is BOAT:
            if pl.drift(0, 1, RAPIDS_SPEED, dt, self.world) and not self.bump_cooldown:
                self.bump_cooldown = 90
                self._toast("Tum! Bateu numa pedra... e a Lara já consertou o casco!")
        if here is Terrain.WIND:
            pl.drift(0, 1, WIND_SPEED, dt, self.world)
            if not self.wind_note:
                self.wind_note = 1
                self._toast("Uuuuu! O vento é forte demais para subir a pé!", 180)

    def _check_exit(self):
        here = self.world.terrain_at_pixel(*self.player.feet)
        if here is Terrain.GATE and self.spec.get("next"):
            self.manager.change(Play(self.spec["next"], self.inventory))

    # ------------------------------------------------------------ conversa e tarefas
    def _interactable_in_front(self):
        for tile in self.player.facing_tiles():
            for obj in self.objects:
                if obj.covers(tile):
                    return obj
        return None

    def _talk(self, obj):
        have = self.inventory.have()
        if obj.kind == "sign":
            self._say("", list(obj.lines))
            return
        if obj.kind == "pickup":
            def take():
                self.inventory.flags.add(obj.item)
                if obj in self.objects:
                    self.objects.remove(obj)
            self._say("", list(obj.lines), take)
            return
        if obj.kind in ("task", "prop"):
            self._do_step(obj, have)
            return
        # npc
        if obj.joins:
            self.inventory.flags.add("falou_" + obj.joins)
        blocked = obj.blocked(have)
        lines = list(obj.current_lines(have))
        if blocked and not obj.missing:
            lines = ["Ainda falta algo para eu poder ajudar."]
        gift = ALL.get(obj.gives) if obj.gives and not obj.given and not blocked else None
        joins = obj.joins if obj.joins and not blocked and obj.joins not in self.inventory.friends else None
        if gift:
            lines.append(f"Vocês ganharam: {gift.name}!")
        if joins and obj.joins != "olivia":
            lines.append(f"{obj.name} entrou para o grupo!")

        def finish():
            if gift:
                self.inventory.add(gift)
                self.inventory.flags.add(gift.key)
                obj.given = True
            if joins:
                self.inventory.join(joins)
            if obj.cutscene and not blocked:
                from src.states.cutscene import Cutscene
                self.manager.change(Cutscene(obj.cutscene, self.inventory))
                return
            if joins or (obj.image and gift):
                if obj in self.objects:
                    self.objects.remove(obj)
                    for t in obj.footprint():
                        self.world.solid_tiles.discard(t)
                self._build_followers()
                for f in self.followers:
                    f.x, f.y = self.player.x, self.player.y
                self.trail.reset(self.player.x, self.player.y)
            if gift is not None and gift.key == "unicorn":
                self.player.switch_transport(gift, self.world)

        self._say(obj.name if not obj.image else "", lines, finish)

    def _do_step(self, obj, have):
        step = obj.next_step(have)
        if step is None:
            if obj.lines:
                self._say("", list(obj.lines))
            return
        if any(n not in have for n in step.needs):
            self._say("", step.missing or ["Ainda falta algo aqui."])
            return

        def finish():
            if step.sets:
                self.inventory.flags.add(step.sets)
            remaining = obj.next_step(self.inventory.have())
            if obj.clear and (remaining is None):
                self._clear(obj.clear)
            if remaining is None and obj.kind == "task":
                obj.done = True
                if obj in self.objects:
                    self.objects.remove(obj)
            if obj.cutscene and remaining is None:
                from src.states.cutscene import Cutscene
                self.manager.change(Cutscene(obj.cutscene, self.inventory))

        self._say("", step.lines, finish)

    def _clear(self, box):
        """Espinheiro resolvido: vira trilha onde a trilha passava, e grama no resto."""
        x0, y0, x1, y1 = box
        g = self.world.grid
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if g[y][x] is not Terrain.THORN:
                    continue
                row = self.world.terrain_at(x0 - 1, y) is Terrain.DIRT and self.world.terrain_at(x1 + 1, y) is Terrain.DIRT
                col = self.world.terrain_at(x, y0 - 1) is Terrain.DIRT and self.world.terrain_at(x, y1 + 1) is Terrain.DIRT
                g[y][x] = Terrain.DIRT if (row or col) else Terrain.GRASS
        self.world.invalidate()

    # ------------------------------------------------------------ desenho
    def _lights(self):
        cam = self.camera
        px, py = self.player.center
        flick = int(math.sin(self.ticks / 7.0) * 3)
        lights = [(px - cam.x, py - cam.y - 6, 128 + flick)]
        for tx, ty in self.lamps:
            x, y = tx * T + T // 2 - cam.x, ty * T + 8 - cam.y
            if -100 < x < W + 100 and -100 < y < H + 100:
                lights.append((x, y, 92 + flick))
        for d in self.decor:
            if getattr(d, "light", 0) and d.glow > 0.25:
                lights.append((d.x - cam.x, d.y - cam.y, d.light))
        for obj in self.objects:
            if obj.kind in ("npc", "pickup", "sign"):
                lights.append((obj.rect.centerx - cam.x, obj.rect.centery - cam.y - 10, 48))
        return lights

    def _draw_card(self, canvas):
        left = CARD_TICKS - self.ticks
        if left < 30 and (left // 3) % 2:
            return
        w, h = 560, 52
        rect = ((W - w) // 2, 26, w, h)
        draw_panel(canvas, rect)
        draw_text(canvas, self.spec["card"], W // 2, 36, P["amarelo"], size=32, center=True)

    def _goal(self):
        have = self.inventory.have()
        for key, text in self.spec.get("goals", []):
            if not key or key not in have:
                return text
        return ""

    def _draw_hud(self, canvas):
        goal = self._goal()
        if goal:
            draw_text(canvas, "Missão: " + goal, 10, 8, P["branco"], size=16, shadow=P["contorno"])
        # relogio do sol ate o jantar
        x0, y0, w = W - 150, 10, 116
        pygame.draw.line(canvas, P["contorno"], (x0, y0 + 13), (x0 + w, y0 + 13), 4)
        pygame.draw.line(canvas, P["areia_clara"], (x0, y0 + 13), (x0 + w, y0 + 13), 2)
        sx = x0 + int(w * self.spec.get("hour", 0.5))
        sy = y0 + 13 - int(math.sin(math.pi * self.spec.get("hour", 0.5)) * 8)
        pygame.draw.circle(canvas, P["contorno"], (sx, sy), 7)
        pygame.draw.circle(canvas, P["amarelo"] if self.spec.get("hour", 0) < 0.8 else P["laranja"], (sx, sy), 5)
        pygame.draw.circle(canvas, P["contorno"], (x0 + w + 14, y0 + 13), 9)                # pratinho do jantar
        pygame.draw.circle(canvas, P["branco"], (x0 + w + 14, y0 + 13), 7)
        pygame.draw.circle(canvas, P["rosa"], (x0 + w + 14, y0 + 13), 3)
        draw_text(canvas, "Jantar", x0 + w - 24, y0 + 18, P["branco"], size=16, shadow=P["contorno"])
        if self.player.transport is not ON_FOOT:
            draw_text(canvas, self.player.transport.name, 10, 26, P["amarelo"], size=16, shadow=P["contorno"])

    def draw(self, canvas):
        canvas.fill(P["contorno"])
        cam = self.camera
        self.world.draw(canvas, cam, self.ticks // 30)
        for layer in ("back", "ground"):
            for d in self.decor:
                if d.layer == layer:
                    d.draw(canvas, cam)
        near = self.player.center
        things = [(o.rect.bottom, 0, o) for o in self.objects]
        riding = self.player.transport is not ON_FOOT
        if not riding:
            things += [(f.y + T, 1, f) for f in self.followers]
        things.append((self.player.y + T + 0.5, 2, self.player))
        for _y, _k, thing in sorted(things, key=lambda t: (t[0], t[1])):
            if thing is self.player or isinstance(thing, Follower):
                thing.draw(canvas, cam)
            else:
                thing.draw(canvas, cam, near, self.ticks)
        for d in self.decor:
            if d.layer == "air":
                d.draw(canvas, cam)
        if self.rain:
            self.rain.draw(canvas)
        if self.wind:
            self.wind.draw(canvas)
        if self.tint:
            self.tint.draw(canvas)
        if self.darkness:
            self.darkness.draw(canvas, self._lights(), self.ticks)
        if self.fog and self.fog_amount > 0.02:
            px, py = self.player.center
            self.fog.draw(canvas, [(px - cam.x, py - cam.y, 170)], self.ticks, self.fog_amount)
        if self.ticks < CARD_TICKS:
            self._draw_card(canvas)
        else:
            self._draw_hud(canvas)
        if self.toast_ticks:
            lines = wrap(self.toast, 32, W - 60)
            for i, line in enumerate(lines):
                y = H - 16 - 34 * (len(lines) - i)
                draw_text(canvas, line, W // 2, y, P["branco"], size=32, center=True, shadow=P["contorno"])
