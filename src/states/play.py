"""Estado Jogando: mundo, camera, a Bela com colisao, inventario e dialogos."""
import pygame

from src import config
from src.entities.player import Player
from src.input import Action
from src.lighting import Darkness, Sunset
from src.maps import MAPS, TRANSITIONS
from src.inventory import Inventory
from src.states.base import State
from src.states.chapter_end import ChapterEnd
from src.states.dialogue import DialogueState
from src.states.cutscene import Cutscene
from src.states.inventory import InventoryState
from src.states.pause import Pause
from src.states.victory import Victory
from src.text import draw_text
from src.transport import ALL
from src.weather import Rain
from src.world.camera import Camera
from src.world.objects import load_creatures, load_decor, load_objects
from src.world.terrain import Terrain
from src.world.tilemap import Tilemap

START_TILE = (24, 15)  # no caminho principal da floresta (usado pelos testes)
CARD_TICKS = 150
INSUMOS = {"dragon": "Dragão"}


class Play(State):
    def __init__(self, map_id="floresta_inicial", spawn=None, inventory=None, transport=None):
        super().__init__()
        spec = MAPS[map_id]
        self.map_id = map_id
        base = spec["base"]
        self.world = Tilemap.load(base + ".map.txt")
        self.objects = load_objects(base + ".objects.json")
        self.decor = load_decor(base + ".decor.json")
        self.creatures = load_creatures(base + ".creatures.json")
        self.toast = ""
        self.toast_ticks = 0
        for obj in self.objects:
            self.world.solid_tiles.add(obj.tile)
        self.camera = Camera(self.world.pixel_w, self.world.pixel_h)
        sx, sy = spawn or spec["spawn"]
        self.player = Player(sx * config.TILE, sy * config.TILE)
        if transport is not None:
            self.player.transport = transport
        self.inventory = inventory or Inventory()
        self.ticks = 0
        self.rain = Rain() if (spec["weather"] == "rain" and config.WEATHER == "rain") else None
        self.darkness = Darkness() if spec["dark"] else None
        self.card = spec["card"]
        self.tint = Sunset() if spec.get("tint") == "sunset" else None
        self.spawn_tile = (sx, sy)
        self.timer_max = int(spec.get("timer", 0)) * 60     # eclipse: contagem regressiva (ticks)
        self.timer = self.timer_max
        self.timer_end_x = spec.get("timer_end_x")      # ao passar desta coluna, o eclipse para
        self.crystals = [(tx, ty) for ty in range(self.world.rows) for tx in range(self.world.cols)
                         if self.world.grid[ty][tx] is Terrain.CRYSTAL]
        self.camera.follow(*self.player.center)

    def update(self, dt, inp):
        self.ticks += 1
        if self.rain:
            self.rain.update()
        if inp.pressed(Action.PAUSE):
            self.manager.push(Pause())
            return
        if inp.pressed(Action.INVENTORY):
            self.manager.push(InventoryState(self))
            return
        if self.toast_ticks:
            self.toast_ticks -= 1
        if self.timer_max and self.timer_end_x and self.player.center[0] >= self.timer_end_x * config.TILE:
            self.timer_max = 0                            # chegou ao acampamento a tempo
            self.toast = "Você chegou ao acampamento a tempo!"
            self.toast_ticks = 150
        if self.timer_max and self.ticks > CARD_TICKS // 2:
            self.timer -= 1
            if self.timer <= 0:                      # o eclipse venceu: recomeca o trecho, sem punicao
                self.player.x = self.spawn_tile[0] * config.TILE
                self.player.y = self.spawn_tile[1] * config.TILE
                self.player.jump_t = -1
                self.timer = self.timer_max
                self.toast = "O tempo acabou! Recomece o trecho."
                self.toast_ticks = 150
        if inp.pressed(Action.INTERACT) and not self.player.jumping:
            target = self._interactable_in_front()
            if target:
                self._talk(target)
                return
            self.player.try_jump(self.world)
        if self.player.jumping:
            self.player.update_jump()
        else:
            dx, dy = inp.direction()
            self.player.move(dx, dy, dt, self.world)
        self.camera.follow(*self.player.center)
        on_lake = self.player.transport.key == "boat"
        if self.rain:
            self.rain.storm = on_lake
        for c in self.creatures:
            if c.update(self.player, self.world):
                self.toast = "O bicho escuro empurrou o barco!"
                self.toast_ticks = 120
        for d in self.decor:
            d.update(self.player.center)
        hx, hy, hw, hh = self.player.hitbox
        here = self.world.terrain_at_pixel(hx + hw / 2, hy + hh / 2)
        dest = TRANSITIONS.get((self.map_id, here))
        if here is Terrain.CASTLE:
            self.manager.change(Victory())
        elif dest:
            self.manager.change(Play(dest[0], dest[1], self.inventory, self.player.transport))
        elif here is Terrain.GATE:
            self.manager.change(ChapterEnd(
                "Capítulo concluído",
                ["Isabela segue viagem rumo ao castelo."]))

    def _lights(self):
        """Luzes em coordenadas de tela: Isabela, cristais visiveis e NPCs."""
        cam = self.camera
        px, py = self.player.center
        lights = [(px - cam.x, py - cam.y, 46, False)]
        half = config.TILE // 2
        for tx, ty in self.crystals:
            x = tx * config.TILE + half - cam.x
            y = ty * config.TILE + half - cam.y
            if -48 < x < config.LOGICAL_W + 48 and -48 < y < config.LOGICAL_H + 48:
                lights.append((x, y, 38, True))
        for obj in self.objects:
            if obj.kind == "npc":
                lights.append((obj.rect.centerx - cam.x, obj.rect.centery - cam.y, 26, False))
        return lights

    def _draw_eclipse(self, canvas):
        """Barra de tempo: esvazia ate o castelo escurecer. Ao zerar, recomeca o trecho."""
        p = config.PALETTE
        w = 90
        x, y = config.LOGICAL_W - w - 6, 6
        frac = max(self.timer, 0) / self.timer_max
        pygame.draw.rect(canvas, p["contorno"], (x - 1, y - 1, w + 2, 8))
        color = p["amarelo"] if frac > 0.34 else p["vermelho"]
        pygame.draw.rect(canvas, color, (x, y, round(w * frac), 6))
        draw_text(canvas, "TEMPO", x - 38, y - 2, p["branco"], size=12, shadow=p["contorno"])

    def _draw_card(self, canvas):
        """Cartao de titulo do capitulo, que some devagar."""
        left = CARD_TICKS - self.ticks
        if left < 30 and (left // 3) % 2:        # pisca ao sumir
            return
        p = config.PALETTE
        w, h = 300, 22
        rect = ((config.LOGICAL_W - w) // 2, 14, w, h)
        pygame.draw.rect(canvas, p["contorno"], rect)
        pygame.draw.rect(canvas, p["areia_clara"], rect, 1)
        draw_text(canvas, self.card, config.LOGICAL_W // 2, 19, p["amarelo"], size=16, center=True)

    def _interactable_in_front(self):
        tiles = self.player.facing_tiles()
        for tile in tiles:
            for obj in self.objects:
                if obj.tile == tile:
                    return obj
        return None

    def _talk(self, obj):
        if obj.kind == "altar":
            if self.inventory.has_all_insumos():
                self.manager.change(Cutscene())
            else:
                n = self.inventory.count_insumos()
                self.manager.push(DialogueState("", [
                    f"Este é o altar das princesas. Ele precisa dos quatro aliados: barco, unicórnio, carro rosa e dragão ({n}/4). Reúna todos antes."]))
            return
        messages = list(obj.current_lines())
        gift = ALL.get(obj.gives) if obj.gives and not obj.given else None
        insumo = INSUMOS.get(obj.gives) if obj.gives and not obj.given and gift is None else None
        if gift:
            messages.append(f"Isabela recebeu: {gift.name}!")
        elif insumo:
            messages.append(f"Isabela ganhou o aliado: {insumo}!")

        def finish():
            if gift:
                self.inventory.add(gift)
                obj.given = True
            elif insumo:
                self.inventory.insumos.add(obj.gives)
                obj.given = True

        speaker = obj.name if obj.kind == "npc" else ""
        self.manager.push(DialogueState(speaker, messages, finish))

    def draw(self, canvas):
        canvas.fill(config.PALETTE["contorno"])
        self.world.draw(canvas, self.camera, self.ticks // 30)
        for layer in ("back", "ground"):
            for d in self.decor:
                if d.layer == layer:
                    d.draw(canvas, self.camera)
        for obj in self.objects:
            obj.draw(canvas, self.camera, self.player.center)
        for c in self.creatures:
            c.draw(canvas, self.camera)
        self.player.draw(canvas, self.camera)
        for d in self.decor:
            if d.layer == "air":
                d.draw(canvas, self.camera)
        if self.rain:
            self.rain.draw(canvas)
        if self.tint:
            self.tint.draw(canvas)
        if self.darkness:
            self.darkness.draw(canvas, self._lights(), self.ticks)
        if self.timer_max:
            self._draw_eclipse(canvas)
        if self.card and self.ticks < CARD_TICKS:
            self._draw_card(canvas)
        if self.toast_ticks:
            draw_text(canvas, self.toast, config.LOGICAL_W // 2, config.LOGICAL_H - 16, config.PALETTE["branco"],
                      size=14, center=True, shadow=config.PALETTE["contorno"])
        draw_text(canvas, self.player.transport.name, 4, 3, config.PALETTE["branco"], size=14,
                  shadow=config.PALETTE["contorno"])
