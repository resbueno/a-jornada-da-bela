"""Cenas animadas: a abertura (castelo tomado) e o final (altar, Dragao, duelo, castelo restaurado).

A cena e um roteiro (gerador Python): cada `yield` espera 1 tick. Z avanca a legenda atual;
Esc/P pula a cena inteira. Usa os mesmos sprites do jogo, com atores se movendo no mapa dos portoes.
"""
import math
import random

import pygame

from src import config
from src.input import Action
from src.sprites import ROOT, character
from src.states.base import State
from src.text import draw_text, wrap
from src.ui import draw_panel
from src.world.objects import Interactable
from src.world.terrain import Terrain
from src.world.tilemap import Tilemap

T = config.TILE
P = config.PALETTE
VW, VH = config.LOGICAL_W, config.LOGICAL_H


class Cam:
    def __init__(self):
        self.x = 0
        self.y = 0


class Actor:
    """Personagem da cena. (x, y) e o canto do tile 16x16; o sprite 16x24 sobe 8 px."""

    def __init__(self, sprite, tx, ty, facing="down", scale=1):
        self.sprite = sprite
        self.x = float(tx * T)
        self.y = float(ty * T)
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
        frames = character(self.sprite)[self.facing]
        surf = frames[1 + (self.walk_ticks // 8) % 2] if self.walking else frames[0]
        if self.scale != 1:
            surf = pygame.transform.scale(surf, (surf.get_width() * self.scale, surf.get_height() * self.scale))
        if self.alpha < 255:
            surf = surf.copy()
            surf.set_alpha(self.alpha)
        x = round(self.x - cam.x) - (surf.get_width() - T) // 2
        y = round(self.y + T - surf.get_height() - self.lift - cam.y)
        canvas.blit(surf, (x, y))


class Cutscene(State):
    MAP = "assets/maps/portoes.map.txt"

    def __init__(self, kind="finale"):
        super().__init__()
        self.kind = kind                      # "finale" ou "intro"
        self.icons = []                       # [x, y, cor, rotulo] fixos na tela (abertura)
        self.world = Tilemap.load(self.MAP)
        self.cam = Cam()
        self.cam_target = (136.0, 92.0)
        self.cam_f = [136.0, 92.0]
        self.ticks = 0
        self.skip_beat = False
        self.caption = ""
        self.caption_ticks = 0
        self.gloom = 105               # veu cinzento da Sombra
        self.flash_a = 0.0
        self.fade_a = 0.0
        self.shake = 0.0
        self.particles = []            # [x, y, vx, vy, vida, vida_max, cor]
        self.rings = []                # [x, y, r, r_max, cor]
        self.beam = None               # (x0, y0, x1, y1, ticks)
        self.orbs = []                 # [x0, y0, x1, y1, t, t_max, cor]
        self.gems = [False] * 4
        self.mode = "exterior"         # "exterior" | "interior"
        self.dragon = None
        self.dragon_pos = [0.0, 0.0]
        self.dragon_alpha = 0
        self.dragon_scale = 0.4
        self.interior_t = 0
        self.rng = random.Random(77)
        self.altar = Interactable("altar", (18, 12), "Altar", [""])
        self.isabela = Actor("isabela", 18, 13, "up")
        self.olivia = Actor("olivia", 12, 17, "right")
        self.lara = Actor("lara", 24, 17, "left")
        self.lana = Actor("lana", 13, 19, "right")
        self.sara = Actor("sara", 23, 19, "left")
        self.princesses = [self.olivia, self.lara, self.lana, self.sara]
        self.villain = Actor("sombra", 0, 0, "down", scale=3)
        self.hero_big = Actor("isabela", 0, 0, "right", scale=3)
        if kind == "intro":
            for y in range(self.world.rows):              # no comeco, o castelo esta livre
                for x in range(self.world.cols):
                    if self.world.grid[y][x] is Terrain.THORN:
                        self.world.grid[y][x] = Terrain.GRASS
            self.gloom = 0
            self.cam_target = (136.0, 24.0)
            self.cam_f = [136.0, 24.0]
            self.isabela.x, self.isabela.y = 17 * T, 19 * T
            self.script = self._script_intro()
        else:
            self.script = self._script()

    def enter(self):
        sheet = pygame.image.load(str(ROOT / "assets" / "sprites" / "dragon.png")).convert_alpha()
        self.dragon = sheet

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

    def move(self, actor, px, py, speed=44.0):
        """Anda ate (px, py) em pixels, primeiro no eixo X e depois no Y."""
        actor.walking = True
        step = speed * config.DT
        for axis in (0, 1):
            while True:
                cur = actor.x if axis == 0 else actor.y
                goal = px if axis == 0 else py
                d = goal - cur
                if abs(d) <= step:
                    if axis == 0:
                        actor.x = goal
                    else:
                        actor.y = goal
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
        """Roda varios geradores ao mesmo tempo ate todos acabarem."""
        gens = list(gens)
        while gens:
            for g in gens[:]:
                try:
                    next(g)
                except StopIteration:
                    gens.remove(g)
            yield

    def burst(self, x, y, colors, n=18, speed=1.6, life=34):
        for _ in range(n):
            a = self.rng.uniform(0, math.tau)
            s = self.rng.uniform(0.4, speed)
            self.particles.append([x, y, math.cos(a) * s, math.sin(a) * s - 0.3, life, life, self.rng.choice(colors)])

    def ring(self, x, y, color, r_max=90):
        self.rings.append([x, y, 4.0, float(r_max), color])

    def fade_to(self, target, ticks=30):
        start = self.fade_a
        for i in range(ticks):
            self.fade_a = start + (target - start) * (i + 1) / ticks
            yield

    def lerp_gloom(self, target, ticks=90):
        start = self.gloom
        for i in range(ticks):
            self.gloom = start + (target - start) * (i + 1) / ticks
            yield

    def jump_cheer(self, actors, ticks=60):
        for i in range(ticks):
            for k, a in enumerate(actors):
                a.lift = abs(math.sin((i + k * 7) / 6.0)) * 7
            yield
        for a in actors:
            a.lift = 0

    # ------------------------------------------------------------ roteiro
    def _script(self):
        altar_c = (18 * T + 8, 12 * T + 8)
        yield from self.say("As cinco princesas se reuniram nos portões do castelo.", 130)
        # as quatro guardiãs chegam ao altar
        spots = [(15, 11), (21, 11), (15, 13), (21, 13)]
        walkers = [self.move(a, s[0] * T, s[1] * T) for a, s in zip(self.princesses, spots)]
        yield from self.together(*walkers)
        self.olivia.facing = "right"; self.lara.facing = "left"; self.lana.facing = "right"; self.sara.facing = "left"
        yield from self.wait(25)
        yield from self.say("Cada uma trouxe um dos quatro aliados.", 120)
        gifts = [(self.olivia, "O barco", "agua"), (self.lara, "O unicórnio", "rosa"),
                 (self.lana, "O carro rosa", "vermelho"), (self.sara, "O dragão", "verde_brilho")]
        for k, (who, label, color) in enumerate(gifts):
            who.lift = 3
            yield from self.say(f"{label} é levado até o altar.", 20)
            self.orbs.append([who.x + 8, who.y - 4, altar_c[0], altar_c[1] - 6, 0, 36, color])
            yield from self.wait(38)
            self.gems[k] = True
            self.burst(altar_c[0], altar_c[1] - 6, [P[color], P["branco"]], 14)
            who.lift = 0
            yield from self.wait(20)
        yield from self.say("Isabela observa, com a espada na cintura.", 110)
        # explosão de luz
        yield from self.say("Juntos, os quatro aliados soltam uma luz muito forte!", 20)
        for i in range(6):
            self.ring(altar_c[0], altar_c[1], [P["branco"], P["amarelo"], P["ceu"]][i % 3], 120 + i * 10)
            self.flash_a = 255
            self.shake = 5
            yield from self.wait(8)
        self.burst(altar_c[0], altar_c[1], [P["branco"], P["amarelo"], P["rosa"], P["ceu"]], 50, 3.2, 50)
        yield from self.wait(50)
        # o dragão desperta
        self.dragon_pos = [altar_c[0] - 24, altar_c[1] - 20]
        for i in range(60):
            u = i / 59
            self.dragon_alpha = int(255 * min(1, u * 2))
            self.dragon_scale = 0.5 + 1.5 * u
            self.dragon_pos[1] = altar_c[1] - 30 - 56 * u
            self.dragon_pos[0] = altar_c[0] - 24 - 70 * u
            self.shake = 2
            yield
        yield from self.say("O dragão acorda e dá um rugido alegre!", 20)
        for _ in range(3):
            self.shake = 6
            self.burst(self.dragon_pos[0] + 90, self.dragon_pos[1] + 36, [P["amarelo"], P["laranja"], P["rosa"]], 10, 2.2, 24)
            yield from self.wait(24)
        # sopro luminoso
        yield from self.say("Ele sopra uma luz colorida e queima a cerca de espinhos!", 15)
        mouth = (self.dragon_pos[0] + 2 * 46, self.dragon_pos[1] + 2 * 17)
        target = (17 * T + 8, 6 * T)
        for i in range(70):
            self.beam = (mouth[0], mouth[1], target[0], target[1], i)
            if i % 3 == 0:
                self.burst(target[0], target[1], [P["branco"], P["rosa"], P["ceu"], P["amarelo"]], 4, 2.0, 24)
            self.shake = 3
            yield
        for y in range(5, 8):                           # espinhos desaparecem
            for x in range(16, 20):
                if self.world.grid[y][x] is Terrain.THORN:
                    self.world.grid[y][x] = Terrain.GRASS
        self.world.invalidate()
        self.burst(target[0], target[1] + 16, [P["roxo"], P["branco"], P["rosa"]], 40, 3.0, 50)
        self.flash_a = 200
        self.beam = None
        yield from self.together(self.lerp_gloom(40, 110), self.jump_cheer(self.princesses, 110))
        yield from self.say("A névoa escura vai embora e o céu fica claro.", 150)
        # a caminhada de Isabela
        yield from self.say("Enquanto as amigas cuidam dos aliados lá fora...", 100)
        self.isabela.facing = "up"
        self.cam_target = (140.0, 60.0)
        yield from self.move(self.isabela, 17 * T, 13 * T, 40)
        yield from self.move(self.isabela, 17 * T, 5 * T, 40)
        yield from self.say("...Isabela entra sozinha no castelo.", 60)
        for i in range(30):
            self.isabela.alpha = 255 - i * 8
            self.isabela.y -= 0.5
            self.isabela.walking = True
            self.isabela.walk_ticks += 1
            yield
        self.isabela.visible = False
        # duelo no salão do trono
        yield from self.fade_to(255, 30)
        self.mode = "interior"
        self.hero_big.x, self.hero_big.y = 40.0, 76.0
        self.hero_big.facing = "right"
        self.villain.x, self.villain.y = 232.0, 76.0
        self.villain.facing = "down"
        self.villain.alpha = 255
        yield from self.fade_to(0, 30)
        yield from self.say("Sombra Cinzenta: \"Este castelo agora é meu!\"", 130)
        yield from self.say("Isabela: \"Não, ele é do povo. Eu vou retomá-lo!\"", 130)
        yield from self.duel()
        yield from self.say("Com um último golpe, a Sombra Cinzenta vai embora para sempre.", 130)
        # castelo restaurado
        yield from self.fade_to(255, 30)
        self.mode = "exterior"
        self.gloom = 0
        self.isabela.visible = True
        self.isabela.alpha = 255
        self.isabela.x, self.isabela.y = 17 * T, 8 * T
        self.isabela.facing = "down"
        self.cam_target = (136.0, 92.0)
        yield from self.fade_to(0, 30)
        yield from self.say("O castelo volta a ser como era antes.", 100)
        for _ in range(4):
            self.burst(self.rng.randint(150, 420), self.rng.randint(60, 150),
                       [P["rosa"], P["amarelo"], P["branco"], P["ceu"], P["verde_brilho"]], 16, 1.8, 50)
            yield from self.wait(22)
        celebrants = [self.isabela] + self.princesses
        yield from self.together(self.move(self.isabela, 18 * T, 13 * T, 50), self.jump_cheer(celebrants, 150))
        yield from self.say("O reino volta a ficar em paz.", 150)
        yield from self.say("Olívia voltou a navegar pelo lago, agora sem medo.", 150)
        yield from self.say("Lara passeia com o unicórnio pelas colinas, e Lana abriu as cavernas para visitas.", 170)
        yield from self.say("Sara cuida do dragão no pátio do castelo.", 140)
        yield from self.say("E Isabela governa o reino ao lado das quatro amigas. Fim.", 200)
        yield from self.fade_to(255, 40)

    def _script_intro(self):
        """Abertura: o castelo em paz, a chegada da Sombra Cinzenta e a partida de Isabela."""
        self.fade_a = 255
        yield from self.fade_to(0, 40)
        yield from self.say("Há muito tempo, o Reino de Cristal vivia em paz.", 150)
        for _ in range(3):
            self.burst(self.rng.randint(150, 420), self.rng.randint(40, 120),
                       [P["rosa"], P["amarelo"], P["branco"]], 10, 1.4, 44)
            yield from self.wait(26)
        yield from self.say("Até que um vilão chamado Sombra Cinzenta tomou o castelo.", 20)
        self.villain.x, self.villain.y = 17 * T + 8, 8 * T
        self.villain.scale = 2
        self.villain.facing = "down"
        self.villain.alpha = 0
        for i in range(90):
            self.villain.alpha = min(255, i * 4)
            self.gloom = min(105, i * 1.2)
            self.shake = 2 if i % 10 < 5 else 0
            yield
        yield from self.wait(60)
        yield from self.say("Ele fechou os portões com uma cerca de espinhos.", 20)
        for y in range(5, 8):
            for x in range(16, 20):
                if self.world.grid[y][x] is Terrain.GRASS:
                    self.world.grid[y][x] = Terrain.THORN
        self.world.invalidate()
        self.burst(17 * T + 8, 6 * T, [P["roxo"], P["rosa_escuro"], P["contorno"]], 40, 2.6, 46)
        self.shake = 7
        yield from self.wait(120)
        yield from self.say("A princesa Isabela voltou para casa e encontrou o castelo trancado.", 20)
        self.isabela.facing = "up"
        self.cam_target = (136.0, 60.0)
        yield from self.move(self.isabela, 17 * T, 10 * T, 38)
        yield from self.wait(60)
        yield from self.say("Sombra Cinzenta: \"Vá embora! Este castelo agora é meu!\"", 150)
        self.shake = 6
        self.burst(17 * T + 8, 8 * T + 8, [P["roxo"], P["rocha_clara"]], 24, 2.4, 40)
        yield from self.say("Isabela foi mandada para longe, mas não desistiu.", 20)
        yield from self.move(self.isabela, 17 * T, 20 * T, 52)
        yield from self.fade_to(255, 36)
        self.villain.visible = False
        self.gloom = 0
        self.isabela.visible = False
        self.icons = [(70, 70, "agua", "Barco"), (130, 70, "rosa", "Unicórnio"),
                      (190, 70, "vermelho", "Carro rosa"), (250, 70, "verde_brilho", "Dragão")]
        self.cam_target = (136.0, 24.0)
        yield from self.fade_to(0, 30)
        yield from self.say("Para voltar, ela precisa de quatro aliados: um barco, um unicórnio, um carro rosa e um dragão.", 230)
        yield from self.say("Cada um está sob os cuidados de uma amiga. A jornada começa!", 150)
        yield from self.fade_to(255, 40)

    def duel(self):
        """Espada contra espada, em tela cheia, com 3x de escala."""
        self.hero_big.x, self.hero_big.y = 40.0, 76.0
        self.hero_big.facing = "right"
        self.villain.x, self.villain.y = 232.0, 76.0
        base_h, base_v = self.hero_big.x, self.villain.x
        for clash in range(3):
            for i in range(30):                            # aproximam-se
                u = i / 29
                self.hero_big.x = base_h + 80 * u
                self.villain.x = base_v - 80 * u
                self.hero_big.walking = True
                self.hero_big.walk_ticks += 1
                yield
            self.hero_big.walking = False
            self.burst(160, 100, [P["branco"], P["amarelo"], P["ceu"]], 22, 2.6, 26)
            self.flash_a = 120
            self.shake = 7
            self.sword_clash = 12
            yield from self.wait(20)
            for i in range(24):                            # recuam
                u = i / 23
                self.hero_big.x = base_h + 80 * (1 - u)
                self.villain.x = base_v - 80 * (1 - u)
                yield
            yield from self.wait(8)
        # golpe final: a sombra se dissolve
        for i in range(30):
            u = i / 29
            self.hero_big.x = base_h + 90 * u
            self.hero_big.walking = True
            self.hero_big.walk_ticks += 1
            yield
        self.hero_big.walking = False
        for i in range(60):
            self.villain.alpha = max(0, 255 - i * 5)
            if i % 2 == 0:
                self.burst(self.villain.x + 24, self.villain.y + 30, [P["roxo"], P["rocha_clara"], P["branco"]], 6, 2.4, 40)
            self.shake = 4
            yield
        self.flash_a = 255
        yield from self.wait(40)

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
        # camera suave
        self.cam_f[0] += (self.cam_target[0] - self.cam_f[0]) * 0.06
        self.cam_f[1] += (self.cam_target[1] - self.cam_f[1]) * 0.06
        # efeitos
        self.shake = max(0.0, self.shake - 0.25)
        self.flash_a = max(0.0, self.flash_a - 7)
        for p in self.particles:
            p[0] += p[2]; p[1] += p[3]; p[3] += 0.03; p[4] -= 1
        self.particles = [p for p in self.particles if p[4] > 0]
        for r in self.rings:
            r[2] += 2.6
        self.rings = [r for r in self.rings if r[2] < r[3]]
        for o in self.orbs:
            o[4] += 1
        self.orbs = [o for o in self.orbs if o[4] < o[5]]

    def _finish(self):
        if self.kind == "intro":
            from src.states.play import Play
            self.manager.change(Play())
        else:
            from src.states.victory import Victory
            self.manager.change(Victory())

    # ------------------------------------------------------------ desenho
    def _overlay(self, canvas, color_name, alpha):
        """Veu de cor com transparencia por superficie (em cache: barato no navegador)."""
        if alpha <= 0:
            return
        key = ("ov", color_name)
        surf = self.__dict__.setdefault("_ov_cache", {}).get(key)
        if surf is None:
            surf = pygame.Surface((VW, VH))
            surf.fill(P[color_name])
            self._ov_cache[key] = surf
        surf.set_alpha(min(255, int(alpha)))
        canvas.blit(surf, (0, 0))

    def _shake_offset(self):
        if self.shake <= 0:
            return 0, 0
        return self.rng.randint(-int(self.shake), int(self.shake)), self.rng.randint(-int(self.shake), int(self.shake))

    def draw(self, canvas):
        sx, sy = self._shake_offset()
        if self.mode == "interior":
            self._draw_interior(canvas, sx, sy)
        else:
            self._draw_exterior(canvas, sx, sy)
        self._draw_effects(canvas, sx, sy)
        self._overlay(canvas, "branco", self.flash_a)
        self._overlay(canvas, "contorno", self.fade_a)
        self._draw_caption(canvas)

    def _draw_exterior(self, canvas, sx, sy):
        cam = self.cam
        cam.x = int(max(0, min(self.cam_f[0], self.world.pixel_w - VW))) + sx
        cam.y = int(max(0, min(self.cam_f[1], self.world.pixel_h - VH))) + sy
        canvas.fill(P["contorno"])
        # o mundo e desenhado com a camera real (limitada), o deslocamento de tremor entra depois
        real = Cam()
        real.x = max(0, min(cam.x, self.world.pixel_w - VW))
        real.y = max(0, min(cam.y, self.world.pixel_h - VH))
        self.world.draw(canvas, real, (self.ticks // 30) % 2)
        self.altar.draw(canvas, real)
        for k, lit in enumerate(self.gems):                      # gemas acesas no altar
            if lit:
                x = 18 * T - real.x + 3 + k * 3
                y = 12 * T - real.y + 5
                c = ("agua", "rosa", "vermelho", "verde_brilho")[k]
                pygame.draw.rect(canvas, P["branco"], (x - 1, y - 1, 4, 4))
                pygame.draw.rect(canvas, P[c], (x, y, 2, 2))
        if self.kind == "intro":
            self.villain.draw(canvas, real)
        actors = sorted([self.isabela] + (self.princesses if self.kind == "finale" else []), key=lambda a: a.y)
        for a in actors:
            a.draw(canvas, real)
        # dragao
        if self.dragon is not None and self.dragon_alpha > 0:
            w = int(48 * 2 * self.dragon_scale / 2)
            h = int(32 * 2 * self.dragon_scale / 2)
            surf = pygame.transform.scale(self.dragon, (max(w, 1) * 1, max(h, 1) * 1))
            surf.set_alpha(self.dragon_alpha)
            bob = int(math.sin(self.ticks / 10.0) * 3)
            canvas.blit(surf, (round(self.dragon_pos[0] - real.x), round(self.dragon_pos[1] - real.y) + bob))
        self._real_cam = real
        self._overlay(canvas, "rocha_contorno", self.gloom)      # veu cinzento da Sombra

    def _draw_interior(self, canvas, sx, sy):
        canvas.fill(P["contorno"])
        # salao do trono: paredes, janela, colunas e piso quadriculado
        pygame.draw.rect(canvas, P["sombra_caverna"] if "sombra_caverna" in P else P["rocha_contorno"], (0, 0, VW, 100))
        pygame.draw.rect(canvas, P["roxo"], (120 + sx, 14 + sy, 80, 56))
        pygame.draw.rect(canvas, P["rosa_escuro"], (126 + sx, 20 + sy, 68, 44))
        pygame.draw.rect(canvas, P["vermelho_escuro"], (136 + sx, 26 + sy, 48, 32))
        for cx in (18, 78, 242, 302):
            pygame.draw.rect(canvas, P["rocha"], (cx - 8 + sx, 0, 16, 100))
            pygame.draw.rect(canvas, P["rocha_clara"], (cx - 8 + sx, 0, 4, 100))
        for y in range(100, VH, 16):
            for x in range(-16, VW + 16, 16):
                c = P["rocha"] if ((x // 16) + (y // 16)) % 2 else P["rocha_contorno"]
                pygame.draw.rect(canvas, c, (x + sx, y + sy, 16, 16))
        # trono ao fundo
        pygame.draw.rect(canvas, P["rocha_contorno"], (140 + sx, 70 + sy, 40, 36))
        pygame.draw.rect(canvas, P["roxo"], (146 + sx, 76 + sy, 28, 30))
        cam = Cam()
        cam.x, cam.y = -sx, -sy
        bob = math.sin(self.ticks / 12.0) * 3
        self.villain.lift = 6 + bob
        self.villain.draw(canvas, cam)
        self.hero_big.draw(canvas, cam)
        # espada de Isabela
        hx = self.hero_big.x + 24 - cam.x
        hy = self.hero_big.y - 14 - cam.y
        swing = getattr(self, "sword_clash", 0)
        if swing:
            self.sword_clash -= 1
        ex = hx + 26 + (8 if swing else 0)
        ey = hy - 6 - (10 if swing else 0)
        pygame.draw.line(canvas, P["branco"], (hx, hy), (ex, ey), 3)
        pygame.draw.line(canvas, P["ceu"], (hx, hy - 1), (ex, ey - 1), 1)
        pygame.draw.rect(canvas, P["amarelo"], (hx - 3, hy - 3, 5, 6))
        self._real_cam = cam

    def _draw_effects(self, canvas, sx, sy):
        cam = getattr(self, "_real_cam", Cam())
        for o in self.orbs:                                       # orbes voando ate o altar
            u = o[4] / o[5]
            x = o[0] + (o[2] - o[0]) * u - cam.x
            y = o[1] + (o[3] - o[1]) * u - math.sin(u * math.pi) * 28 - cam.y
            pygame.draw.circle(canvas, P[o[6]], (round(x), round(y)), 4)
            pygame.draw.circle(canvas, P["branco"], (round(x), round(y)), 2)
        for r in self.rings:
            alpha = max(0, 1 - r[2] / r[3])
            if alpha > 0:
                pygame.draw.circle(canvas, P[r[4]] if isinstance(r[4], str) else r[4],
                                   (round(r[0] - cam.x), round(r[1] - cam.y)), int(r[2]), 2)
        if self.beam:                                              # sopro neon do dragao
            x0, y0, x1, y1, i = self.beam
            u = min(1.0, i / 18.0)
            ex = x0 + (x1 - x0) * u
            ey = y0 + (y1 - y0) * u
            for k, (c, w) in enumerate((("rosa", 9), ("amarelo", 6), ("ceu", 4), ("branco", 2))):
                pygame.draw.line(canvas, P[c], (round(x0 - cam.x), round(y0 - cam.y)),
                                 (round(ex - cam.x), round(ey - cam.y)), w + int(math.sin(i / 2 + k) * 1))
        for x, y, color, label in self.icons:                       # os quatro aliados (abertura)
            bob = int(math.sin(self.ticks / 14.0 + x) * 3)
            pygame.draw.circle(canvas, P["contorno"], (x, y + bob), 12)
            pygame.draw.circle(canvas, P[color], (x, y + bob), 10)
            pygame.draw.circle(canvas, P["branco"], (x - 3, y + bob - 3), 3)
            draw_text(canvas, label, x, y + 18, P["branco"], size=14, center=True, shadow=P["contorno"])
        for p in self.particles:
            x, y = round(p[0] - cam.x), round(p[1] - cam.y)
            c = p[6]
            canvas.fill(c, (x, y, 2, 2))

    def _draw_caption(self, canvas):
        if not self.caption:
            return
        self.caption_ticks += 1
        box = (6, VH - 40, VW - 12, 34)
        draw_panel(canvas, box)
        lines = wrap(self.caption, 16, box[2] - 16)[:2]
        shown = int(self.caption_ticks * 0.9)
        y = box[1] + 6
        for line in lines:
            part = line[:shown]
            shown -= len(line)
            draw_text(canvas, part, box[0] + 8, y, P["areia_clara"], size=16)
            y += 13
            if shown <= 0:
                break
        if (self.ticks // 25) % 2 == 0:
            draw_text(canvas, "Z", VW - 20, VH - 14, P["rosa"], size=12)
