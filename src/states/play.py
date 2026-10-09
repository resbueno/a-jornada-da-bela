"""Estado Jogando: mundo, camera, a Bela com colisao, inventario e dialogos."""
from src import config
from src.entities.player import Player
from src.input import Action
from src.inventory import Inventory
from src.states.base import State
from src.states.chapter_end import ChapterEnd
from src.states.dialogue import DialogueState
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

START_TILE = (24, 15)  # no caminho principal
MAP = "assets/maps/floresta_inicial"


class Play(State):
    def __init__(self):
        super().__init__()
        self.world = Tilemap.load(MAP + ".map.txt")
        self.objects = load_objects(MAP + ".objects.json")
        self.decor = load_decor(MAP + ".decor.json")
        self.creatures = load_creatures(MAP + ".creatures.json")
        self.toast = ""
        self.toast_ticks = 0
        for obj in self.objects:
            self.world.solid_tiles.add(obj.tile)
        self.camera = Camera(self.world.pixel_w, self.world.pixel_h)
        self.player = Player(START_TILE[0] * config.TILE, START_TILE[1] * config.TILE)
        self.inventory = Inventory()
        self.ticks = 0
        self.rain = Rain() if config.WEATHER == "rain" else None
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
                self.toast = "A criatura corrompida empurrou o barco!"
                self.toast_ticks = 120
        for d in self.decor:
            d.update(self.player.center)
        hx, hy, hw, hh = self.player.hitbox
        here = self.world.terrain_at_pixel(hx + hw / 2, hy + hh / 2)
        if here is Terrain.CASTLE:
            self.manager.change(Victory())
        elif here is Terrain.CAVE:
            self.manager.change(ChapterEnd(
                "Capítulo 2 concluído",
                ["Isabela saltou a fenda e chegou à entrada",
                 "das Cavernas de Quartzo.",
                 "A Princesa Lana espera lá dentro...",
                 "(o capítulo 3 ainda será construído)"]))

    def _interactable_in_front(self):
        tiles = self.player.facing_tiles()
        for tile in tiles:
            for obj in self.objects:
                if obj.tile == tile:
                    return obj
        return None

    def _talk(self, obj):
        messages = list(obj.current_lines())
        gift = ALL.get(obj.gives) if obj.gives and not obj.given else None
        if gift:
            messages.append(f"Bela recebeu: {gift.name}!")

        def finish():
            if gift:
                self.inventory.add(gift)
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
            obj.draw(canvas, self.camera)
        for c in self.creatures:
            c.draw(canvas, self.camera)
        self.player.draw(canvas, self.camera)
        for d in self.decor:
            if d.layer == "air":
                d.draw(canvas, self.camera)
        if self.rain:
            self.rain.draw(canvas)
        if self.toast_ticks:
            draw_text(canvas, self.toast, config.LOGICAL_W // 2, config.LOGICAL_H - 16, config.PALETTE["branco"],
                      size=14, center=True, shadow=config.PALETTE["contorno"])
        draw_text(canvas, self.player.transport.name, 4, 3, config.PALETTE["branco"], size=14,
                  shadow=config.PALETTE["contorno"])
