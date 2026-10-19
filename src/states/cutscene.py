"""Cenas animadas: a abertura, a viagem na Maria Fumaca e o final (o dragao, o portao e o banquete).

A cena e um roteiro (gerador Python): cada `yield` espera 1 tick. Z avanca a legenda atual;
Esc/P pula a cena inteira.
"""
import math
import random

import pygame

from src import config
from src.input import Action
from src.inventory import Inventory
from src.scenery import draw_panorama, rail_point
from src.sprites import character, frames
from src.states.base import State
from src.text import draw_text, wrap
from src.ui import draw_panel
from src.world.tilemap import Tilemap

T = config.TILE
P = config.PALETTE
W, H = config.LOGICAL_W, config.LOGICAL_H
SMOKE = ("rosa", "amarelo", "ceu", "verde_brilho", "roxo", "branco")


class Cam:
    def __init__(self, x=0, y=0):
        self.x, self.y = x, y


class Actor:
    """Personagem da cena. (x, y) e o canto do tile; o sprite sobe para ficar de pe nele."""

    def __init__(self, sprite, tx, ty, facing="down", scale=1):
        self.sprite = sprite
        self.x, self.y = float(tx * T), float(ty * T)
        self.facing = facing
        self.walking = False
        self.walk_ticks = 0
        self.lift = 0.0
        self.alpha = 255
        self.scale = scale
        self.visible = True

    def draw(self, canvas, cam):
        if not self.visible or self.alpha <= 0:
            return
        fr = character(self.sprite)[self.facing]
        surf = fr[1 + (self.walk_ticks // 8) % 2] if self.walking else fr[0]
        if self.scale != 1:
            surf = pygame.transform.scale(surf, (surf.get_width() * self.scale, surf.get_height() * self.scale))
        if self.alpha < 255:
            surf = surf.copy()
            surf.set_alpha(self.alpha)
        x = round(self.x - cam.x) - (surf.get_width() - T) // 2
        y = round(self.y + T - surf.get_height() - self.lift - cam.y)
        canvas.blit(surf, (x, y))


class Cutscene(State):
    def __init__(self, kind="intro", inventory=None):
        super().__init__()
        self.kind = kind
        self.inventory = inventory or Inventory()
        self.ticks = 0
        self.skip_beat = False
        self.caption = ""
        self.caption_ticks = 0
        self.flash_a = 0.0
        self.fade_a = 0.0
        self.shake = 0.0
        self.particles = []            # [x, y, vx, vy, vida, vida_max, cor, tamanho]
        self.rng = random.Random(77)
        self.mode = "panorama"         # "panorama" | "castle" | "banquet"
        self.sky = "tarde"
        self.actors = []
        self.train_u = None
        self.highlight = None          # (x, y): brilho apontando algo na paisagem
        self.labels = []               # [(x, y, texto)]
        self.world = None
        self.cam = Cam()
        self.dragon = None
        if kind == "intro":
            self.script = self._intro()
        elif kind == "train":
            self.sky = "entardecer"
            self.script = self._train()
        else:
            self._setup_castle()
            self.script = self._final()

    # ------------------------------------------------------------ utilidades do roteiro
    def wait(self, n):
        for _ in range(n):
            if self.skip_beat:
                self.skip_beat = False
                return
            yield

    def say(self, text, ticks=170):
        self.caption = text
        self.caption_ticks = 0
        yield from self.wait(ticks)

    def move(self, actor, px, py, speed=88.0):
        """Anda ate (px, py) em pixels, primeiro no eixo X e depois no Y."""
        actor.walking = True
        step = speed * config.DT
        for axis in (0, 1):
            while True:
                cur = actor.x if axis == 0 else actor.y
                goal = px if axis == 0 else py
                d = goal - cur
                if abs(d) <= step:
                    setattr(actor, "x" if axis == 0 else "y", goal)
                    break
                sgn = 1 if d > 0 else -1
                if axis == 0:
                    actor.x += sgn * step
                    actor.facing = "right" if sgn > 0 else "left"
                else:
                    actor.y += sgn * step
                    actor.facing = "down" if sgn > 0 else "up"
                actor.walk_ticks += 1
                yield
        actor.walking = False

    def together(self, *gens):
        gens = list(gens)
        while gens:
            for g in gens[:]:
                try:
                    next(g)
                except StopIteration:
                    gens.remove(g)
            yield

    def burst(self, x, y, colors, n=18, speed=3.2, life=40, size=4):
        for _ in range(n):
            a = self.rng.uniform(0, math.tau)
            s = self.rng.uniform(0.6, speed)
            self.particles.append([x, y, math.cos(a) * s, math.sin(a) * s - 0.6, life, life,
                                   P[self.rng.choice(colors)], size])

    def puff(self, x, y):
        """Nuvem de fumaca colorida subindo."""
        self.particles.append([x, y, self.rng.uniform(-0.4, 0.4), -self.rng.uniform(0.6, 1.2), 90, 90,
                               P[self.rng.choice(SMOKE)], -self.rng.randint(5, 9)])

    def fade_to(self, target, ticks=30):
        start = self.fade_a
        for i in range(ticks):
            self.fade_a = start + (target - start) * (i + 1) / ticks
            yield

    def hop(self, actors, ticks=90):
        for i in range(ticks):
            for k, a in enumerate(actors):
                a.lift = abs(math.sin((i + k * 7) / 6.0)) * 14
            yield
        for a in actors:
            a.lift = 0

    # ------------------------------------------------------------ abertura
    def _intro(self):
        self.fade_a = 255
        yield from self.fade_to(0, 40)
        yield from self.say("Era uma tarde bonita no reino.", 130)
        yield from self.say("A Princesa Isabela, a Bela, passou o dia inteiro brincando do outro lado do reino.", 190)
        self.highlight = (470, 70)
        yield from self.say("Lá no alto da montanha, o castelo prepara o Grande Banquete Real.", 180)
        yield from self.say("O jantar começa ao pôr do sol... e o caminho de volta é cheio de obstáculos!", 190)
        self.highlight = None
        self.labels = [(60, 300, "Bosque"), (250, 344, "Vale"), (330, 236, "Montanha"), (470, 140, "Castelo")]
        yield from self.say("Um bosque escuro, um rio sem ponte e uma montanha cheia de vento.", 200)
        self.labels = []
        names = ("isabela", "lana", "lara", "olivia")
        self.actors = [Actor(n, -2 - i * 1.4, 0, "right") for i, n in enumerate(names)]
        for a in self.actors:
            a.y = 214.0
        walk = [self.move(a, 150 + i * 70, a.y, 110) for i, a in enumerate(self.actors)]
        yield from self.say("Mas a Bela não vai sozinha: as melhores amigas vão ajudar!", 0)
        yield from self.together(*walk)
        for a in self.actors:
            a.facing = "down"
        yield from self.wait(90)
        bela = self.actors[0]
        self.burst(bela.x + 16, bela.y - 10, ("rosa", "amarelo", "branco"), 24, 2.4, 50)
        yield from self.say("E ela leva a Lanterna do Coração, que ilumina e aquece. A jornada começa!", 190)
        yield from self.fade_to(255, 40)

    # ------------------------------------------------------------ viagem de trem
    def _train(self):
        self.fade_a = 255
        self.train_u = 0.0
        yield from self.fade_to(0, 30)
        yield from self.say("Piiii-uíí!", 70)
        yield from self.say("A Maria Fumaça acorda, solta nuvens de fumaça coloridas...", 0)
        n = 520
        for i in range(n):
            self.train_u = i / (n - 1)
            if i % 7 == 0:
                x, y, _a, _b = rail_point(self.train_u)
                self.puff(x - 10, y - 26)
            if i == 200:
                self.caption, self.caption_ticks = "...e puxa as meninas montanha acima, contra o vento!", 0
            if i == 380:
                self.caption, self.caption_ticks = "Olívia toca a flauta junto com o apito: Piiii-uíí!", 0
            yield
        self.burst(470, 100, ("rosa", "amarelo", "branco", "ceu"), 40, 3.0, 60)
        yield from self.say("Chegaram ao castelo!", 110)
        yield from self.fade_to(255, 40)

    # ------------------------------------------------------------ final
    def _setup_castle(self):
        from src.maps import sprite_for
        self.mode = "castle"
        self.world = Tilemap.load("assets/maps/castelo.map.txt")
        self.world.style = "castelo"
        self.cam = Cam(0, 0)
        self.dragon = frames("dragon_sleep", 192)
        self.dragon_pos = [13 * T, 6 * T]
        self.dragon_frame = 0
        spots = [("isabela", 15, 10), ("lana", 13, 10), ("lara", 17, 10), ("olivia", 19, 10)]
        self.actors = [Actor(sprite_for(n, "castelo"), x, y, "up") for n, x, y in spots]

    def _final(self):
        yield from self.say("O dragão sente o calorzinho da lanterna...", 110)
        start = self.dragon_pos[0]
        for i in range(140):                                    # rola devagar para o lado
            u = i / 139
            self.dragon_pos[0] = start + 7 * T * (u * u * (3 - 2 * u))
            self.dragon_pos[1] = 6 * T + math.sin(u * math.pi * 3) * -6
            self.shake = 2
            if i % 10 == 0:
                self.burst(self.dragon_pos[0] + 60, self.dragon_pos[1] + 120, ("rocha_clara", "branco"), 4, 1.6, 26)
            yield
        self.dragon_frame = 2
        yield from self.say("...rola devagarinho para o cantinho quentinho e abre os olhos, feliz.", 150)
        for _ in range(3):
            self.burst(self.dragon_pos[0] + 40, self.dragon_pos[1] + 40, ("rosa", "branco"), 8, 1.8, 50)
            yield from self.wait(20)
        yield from self.say("Dragão: \"Ahhh, que soninho bom! Eu estava no caminho? Desculpem!\"", 170)
        yield from self.say("Bela: \"Tudo bem! Quer jantar com a gente?\"   Dragão: \"Oba!\"", 170)
        # o portao se abre
        self.world.gate_open = True
        self.world.invalidate()
        self.flash_a = 200
        self.burst(16 * T, 4 * T, ("amarelo", "branco", "rosa"), 40, 3.4, 50)
        yield from self.say("O portão do castelo se abre!", 100)
        walkers = [self.move(a, (14 + i) * T, 4 * T, 80) for i, a in enumerate(self.actors)]
        yield from self.together(*walkers)
        yield from self.fade_to(255, 36)
        self.mode = "banquet"
        self._setup_banquet()
        yield from self.fade_to(0, 36)
        yield from self.say("No salão, o Grande Banquete Real está servido.", 160)
        yield from self.say("Bela, Lana, Lara e Olívia chegaram bem na hora do jantar!", 170)
        yield from self.say("A Tia Evelyn entrega a encomenda: um laço novo para a Bela!", 170)
        for _ in range(4):
            self.burst(self.rng.randint(80, 560), self.rng.randint(40, 140),
                       ("rosa", "amarelo", "branco", "ceu", "verde_brilho"), 16, 2.6, 60)
            yield from self.wait(18)
        yield from self.together(self.hop(self.actors, 120), self.say("E o dragão? Ganhou o maior prato de todos!", 170))
        yield from self.say("Fim.", 140)
        yield from self.fade_to(255, 40)

    def _setup_banquet(self):
        guests = [("tia_dani", 2, 3.6), ("tio_vitor", 4, 3.6), ("evelyn", 6, 3.6), ("william", 8, 3.6),
                  ("rui", 12, 3.6), ("teo", 14, 3.6), ("jhonny", 15, 3.6), ("lola", 16, 3.6), ("bruce", 17, 3.6)]
        self.guests = [Actor(n, x, y, "down") for n, x, y in guests]
        for k, a in enumerate(self.actors):
            a.x, a.y, a.facing = (6 + k * 2) * T, 218.0, "up"
            a.walking = False

    # ------------------------------------------------------------ ciclo
    def update(self, dt, inp):
        self.ticks += 1
        if inp.pressed(Action.PAUSE):
            self._finish()
            return
        if inp.pressed(Action.INTERACT):
            self.skip_beat = True
        try:
            next(self.script)
        except StopIteration:
            self._finish()
            return
        self.shake = max(0.0, self.shake - 0.25)
        self.flash_a = max(0.0, self.flash_a - 7)
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            if p[7] > 0:
                p[3] += 0.05                  # brilhos caem
            p[4] -= 1
        self.particles = [p for p in self.particles if p[4] > 0]

    def _finish(self):
        from src.states.play import Play
        if self.kind == "intro":
            self.manager.change(Play("bosque"))
        elif self.kind == "train":
            self.manager.change(Play("castelo", self.inventory))
        else:
            from src.states.victory import Victory
            self.manager.change(Victory())

    # ------------------------------------------------------------ desenho
    def _overlay(self, canvas, color_name, alpha):
        if alpha <= 0:
            return
        cache = self.__dict__.setdefault("_ov", {})
        surf = cache.get(color_name)
        if surf is None:
            surf = cache[color_name] = pygame.Surface((W, H))
            surf.fill(P[color_name])
        surf.set_alpha(min(255, int(alpha)))
        canvas.blit(surf, (0, 0))

    def draw(self, canvas):
        sx = self.rng.randint(-int(self.shake), int(self.shake)) if self.shake >= 1 else 0
        if self.mode == "panorama":
            self._draw_panorama(canvas)
        elif self.mode == "castle":
            self._draw_castle(canvas, sx)
        else:
            self._draw_banquet(canvas)
        for x, y, _vx, _vy, life, life_max, color, size in self.particles:
            if size < 0:                                       # fumaca: cresce e some
                r = int(-size + (1 - life / life_max) * 10)
                pygame.draw.circle(canvas, color, (int(x), int(y)), r)
                pygame.draw.circle(canvas, P["branco"], (int(x) - r // 3, int(y) - r // 3), max(1, r // 3))
            else:
                canvas.fill(color, (int(x) - self.cam.x, int(y) - self.cam.y, size, size))
        self._overlay(canvas, "branco", self.flash_a)
        self._overlay(canvas, "contorno", self.fade_a)
        self._draw_caption(canvas)

    def _draw_panorama(self, canvas):
        draw_panorama(canvas, self.sky, self.ticks)
        if self.highlight and (self.ticks // 12) % 2:
            x, y = self.highlight
            pygame.draw.circle(canvas, P["amarelo"], (x, y), 60, 3)
        for x, y, text in self.labels:
            draw_text(canvas, text, x, y, P["branco"], size=32, center=True, shadow=P["contorno"])
        if self.train_u is not None:
            x, y, ang, back = rail_point(self.train_u)
            img = frames("maria_fumaca", 160)[(self.ticks // 6) % 2]
            img = pygame.transform.scale(img, (64, 38))
            if not back:
                img = pygame.transform.flip(img, True, False)
            img = pygame.transform.rotate(img, ang if not back else ang - 180)
            canvas.blit(img, (int(x) - img.get_width() // 2, int(y) - img.get_height() + 6))
        for a in self.actors:
            a.draw(canvas, Cam())

    def _draw_castle(self, canvas, sx):
        canvas.fill(P["contorno"])
        cam = Cam(16 * T - W // 2 + sx, 3 * T)
        self.cam = cam
        self.world.draw(canvas, cam, self.ticks // 30)
        img = self.dragon[self.dragon_frame if self.dragon_frame == 2 else (self.ticks // 50) % 2]
        canvas.blit(img, (round(self.dragon_pos[0]) - cam.x, round(self.dragon_pos[1]) + 4 * T - img.get_height() - cam.y))
        for a in sorted(self.actors, key=lambda a: a.y):
            a.draw(canvas, cam)

    def _draw_banquet(self, canvas):
        self.cam = Cam()
        canvas.fill(P["rocha_contorno"])
        canvas.fill(P["rosa_escuro"], (0, 0, W, 150))                       # parede com cortinas
        for x in range(0, W, 80):
            pygame.draw.rect(canvas, P["vermelho_escuro"], (x, 0, 22, 150))
            pygame.draw.rect(canvas, P["vermelho"], (x + 4, 0, 6, 150))
        pygame.draw.rect(canvas, P["contorno"], (238, 14, 164, 104))         # janelao com o por do sol
        for i, c in enumerate(("roxo", "rosa_escuro", "laranja", "amarelo")):
            canvas.fill(P[c], (242, 18 + i * 25, 156, 25))
        head = frames("dragon_sleep", 192)[2].subsurface((0, 30, 90, 80))  # o dragao espiando pela janela
        canvas.blit(head, (300, 40))
        pygame.draw.rect(canvas, P["madeira_escura"], (238, 64, 164, 4))
        pygame.draw.rect(canvas, P["madeira_escura"], (318, 14, 4, 104))
        for y in range(150, H, 32):                                           # piso quadriculado
            for x in range(0, W, 32):
                c = P["rocha_clara"] if ((x // 32) + (y // 32)) % 2 else P["rocha"]
                canvas.fill(c, (x, y, 32, 32))
        for a in self.guests:                                                 # convidados atras da mesa
            a.lift = 3 if ((self.ticks // 20) + int(a.x)) % 2 else 0
            a.draw(canvas, Cam())
        pygame.draw.rect(canvas, P["contorno"], (20, 146, 600, 56))          # mesa comprida
        pygame.draw.rect(canvas, P["branco"], (24, 146, 592, 40))
        pygame.draw.rect(canvas, P["agua_clara"], (24, 182, 592, 4))
        for k in range(9):                                                    # pratos, comida e velas
            x = 50 + k * 66
            pygame.draw.ellipse(canvas, P["rocha_clara"], (x - 14, 156, 28, 14))
            pygame.draw.ellipse(canvas, P[("laranja", "vermelho", "verde_medio", "amarelo")[k % 4]], (x - 8, 156, 16, 9))
            if k % 3 == 1:
                canvas.fill(P["areia_clara"], (x + 20, 136, 4, 14))
                flame = P["amarelo"] if (self.ticks // 8 + k) % 2 else P["laranja"]
                canvas.fill(flame, (x + 20, 130, 4, 6))
        pygame.draw.ellipse(canvas, P["areia"], (282, 142, 76, 26))           # bolo no meio
        pygame.draw.rect(canvas, P["rosa"], (292, 120, 56, 30))
        pygame.draw.rect(canvas, P["branco"], (292, 120, 56, 6))
        canvas.fill(P["vermelho"], (318, 112, 6, 8))
        for a in self.actors:
            a.draw(canvas, Cam())

    def _draw_caption(self, canvas):
        if not self.caption:
            return
        self.caption_ticks += 1
        box = (12, H - 100, W - 24, 92)
        draw_panel(canvas, box)
        lines = wrap(self.caption, 32, box[2] - 40)[:2]
        shown = int(self.caption_ticks * 0.9)
        y = box[1] + 12
        for line in lines:
            part = line[:shown]
            shown -= len(line)
            draw_text(canvas, part, box[0] + 20, y, P["areia_clara"], size=32)
            y += 34
            if shown <= 0:
                break
        if (self.ticks // 25) % 2 == 0:
            draw_text(canvas, "Z", W - 40, H - 34, P["rosa"], size=16)
