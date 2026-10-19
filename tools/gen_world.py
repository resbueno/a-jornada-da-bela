#!/usr/bin/env python3
"""Gera os 4 mapas da jornada (assets/maps/<id>.map.txt, .objects.json, .decor.json).

bosque   : Bosque dos Sussurros. Vila do Bosque, Lana, espinheiros, o unicornio perdido e o desfiladeiro.
vale     : Vale dos Corregos. Prado na chuva, Lara e os materiais do barco, rio largo e corredeiras.
montanha : Montanha dos Ventos. Estacao, Maria Fumaca, Olivia, galhos altos e a trilha de vento.
castelo  : Portao do Castelo. O dragao sonolento na frente do portao.
Deterministico (seeds fixas). Uso: python3 tools/gen_world.py
"""
import json
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "assets" / "maps"
LEGEND = ("; g chao  h grama alta  f flores  d trilha  s pedra  ~ agua  v corredeira  # pinheiro (2x2)  "
          "r pedra  x desfiladeiro  Y espinheiro  W paredao  w vento  = trilho  k tabuas  p pilar  "
          "L lampiao  K muralha  C portao  G passagem")


class Map:
    def __init__(self, w, h, fill="g", seed=1):
        self.w, self.h = w, h
        self.g = [[fill] * w for _ in range(h)]
        self.rng = random.Random(seed)
        self.reserved = set()
        self.objects, self.decor = [], []

    def rect(self, x0, y0, x1, y1, ch):
        for y in range(max(y0, 0), min(y1, self.h - 1) + 1):
            for x in range(max(x0, 0), min(x1, self.w - 1) + 1):
                self.g[y][x] = ch

    def at(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else "#"

    def reserve(self, x0, y0, x1, y1):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.reserved.add((x, y))

    def forest(self, density=0.85, keep="g"):
        """Enche de pinheiros 2x2 (alinhados em coordenadas pares) tudo que for `keep` e livre."""
        for by in range(0, self.h - 1, 2):
            for bx in range(0, self.w - 1, 2):
                cells = [(bx, by), (bx + 1, by), (bx, by + 1), (bx + 1, by + 1)]
                if all(self.at(x, y) == keep and (x, y) not in self.reserved for x, y in cells):
                    if self.rng.random() < density:
                        for x, y in cells:
                            self.g[y][x] = "#"

    def scatter(self, ch, n, box, on="g"):
        x0, y0, x1, y1 = box
        placed = 0
        for _ in range(n * 40):
            if placed >= n:
                break
            x, y = self.rng.randint(x0, x1), self.rng.randint(y0, y1)
            if self.g[y][x] == on and (x, y) not in self.reserved:
                self.g[y][x] = ch
                placed += 1

    def obj(self, **o):
        o["tile"] = list(o["tile"])
        self.objects.append(o)
        x, y = o["tile"]
        w, h = o.get("size", (1, 1))
        self.reserve(x - 1, y - 1, x + w, y + h)

    def deco(self, kind, x, y):
        self.decor.append({"kind": kind, "tile": [x, y]})

    def free(self, box, on="g", n=1):
        out = []
        x0, y0, x1, y1 = box
        for _ in range(400):
            x, y = self.rng.randint(x0, x1), self.rng.randint(y0, y1)
            if self.g[y][x] == on and (x, y) not in self.reserved and [x, y] not in [d["tile"] for d in self.decor]:
                out.append((x, y))
                if len(out) >= n:
                    break
        return out

    def save(self, name, note):
        (ROOT / f"{name}.map.txt").write_text(
            f"; {note} {self.w}x{self.h}\n{LEGEND}\n" + "\n".join("".join(r) for r in self.g) + "\n", encoding="utf-8")
        (ROOT / f"{name}.objects.json").write_text(
            json.dumps(self.objects, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        (ROOT / f"{name}.decor.json").write_text(json.dumps(self.decor, indent=1) + "\n", encoding="utf-8")
        print(f"{name}: {self.w}x{self.h}, {len(self.objects)} objetos, {len(self.decor)} enfeites")


def sign(m, x, y, text):
    m.obj(kind="sign", tile=(x, y), name="Placa", lines=[text])


# =========================================================================== Mundo 1
def bosque():
    m = Map(58, 40, seed=101)
    # trilhas
    m.rect(4, 26, 21, 37, "g")                       # Vila do Bosque (clareira)
    m.rect(11, 17, 12, 26, "d")                      # trilha da vila para o norte
    m.rect(11, 17, 44, 18, "d")                      # trilha leste
    m.rect(43, 5, 44, 18, "d")                       # sobe ate o bosque escuro
    m.rect(38, 3, 49, 9, "g")                        # clareira do unicornio
    m.rect(50, 0, 51, 39, "x")                       # o grande desfiladeiro
    m.rect(52, 5, 56, 8, "g"); m.rect(52, 6, 56, 7, "d")
    m.rect(56, 6, 57, 7, "G")                        # passagem para o vale
    m.rect(7, 31, 18, 32, "d"); m.rect(11, 27, 12, 37, "d")      # ruas da vila
    for x, y in ((6, 28), (17, 28), (6, 35), (17, 35), (13, 22), (24, 16), (36, 16)):
        m.g[y][x] = "L"                              # lampioes
    m.rect(14, 34, 16, 36, "f"); m.rect(5, 33, 7, 34, "f"); m.rect(15, 27, 16, 28, "f")
    m.rect(20, 19, 30, 21, "h"); m.rect(38, 12, 42, 14, "h")
    # espinheiros: muralha na trilha leste e outra antes da clareira do unicornio
    m.rect(32, 14, 33, 21, "Y")
    m.rect(36, 10, 49, 11, "Y")
    for box in ((4, 26, 21, 37), (10, 16, 45, 19), (42, 4, 45, 18), (37, 2, 50, 10), (50, 1, 57, 9)):
        m.reserve(*box)
    m.reserve(19, 19, 31, 22)
    m.forest(0.92)
    # moldura de arvores nas bordas (fora a passagem)
    m.scatter("r", 18, (2, 2, 48, 38))
    m.scatter("h", 30, (2, 2, 48, 38))

    m.obj(kind="npc", tile=(28, 16), name="Lana", sprite="lana_bosque", joins="lana",
          lines=["Bela! Que bom que você veio. Eu também quero voltar ao castelo a tempo do jantar.",
                 "Mas olha só: espinheiros mágicos fecharam a trilha. Eu trouxe minha corda!",
                 "Vamos juntas? Fique de frente para os espinhos e aperte A: eu puxo os galhos."])
    m.obj(kind="task", tile=(32, 17), name="Espinheiro", clear=[32, 14, 33, 21],
          steps=[dict(needs=["lana"], sets="espinho1",
                      lines=["Lana joga a corda nos galhos espinhosos e puxa com força...",
                             "Lana: \"Upa! Pronto, o caminho está livre!\""],
                      missing=["Espinhos mágicos fecham a trilha. Sozinha, a Bela não consegue tirar."])])
    m.obj(kind="task", tile=(43, 11), name="Espinheiro", clear=[36, 10, 49, 11],
          steps=[dict(needs=["lana"], sets="espinho2",
                      lines=["Lana laça mais um espinheiro e puxa: os galhos vão para o lado.",
                             "Lana: \"Escutou? Alguém está chorando baixinho lá na frente...\""],
                      missing=["Mais espinhos. A Lana e a corda dela fariam falta aqui."])])
    m.obj(kind="npc", tile=(45, 5), name="Unicórnio", image="vehicle_unicorn_side", image_w=64, scared=True,
          gives="unicorn", requires=["lana"],
          missing=["Um unicórnio pequeno treme no escuro. Ele se assusta com a Bela sozinha."],
          lines=["Um unicórnio pequenininho está perdido e com medo do escuro.",
                 "Bela acende a Lanterna do Coração. A luz quentinha deixa tudo mais calmo.",
                 "Unicórnio: \"Hiiin...\" Ele chega pertinho e encosta o focinho na mão da Bela.",
                 "Lana: \"Ele quer ajudar! Vamos subir nas costas dele.\"",
                 "Fique de frente para o desfiladeiro e aperte A para o unicórnio pular!"])
    sign(m, 9, 30, "Vila do Bosque. A trilha do norte leva ao Bosque dos Sussurros.")
    sign(m, 13, 19, "Bosque dos Sussurros. Leve uma luz: aqui é sempre escuro.")
    sign(m, 46, 7, "O Grande Desfiladeiro. Só quem sabe pular atravessa.")
    # moradores da vila
    m.obj(kind="npc", tile=(8, 29), name="Teo", sprite="teo",
          lines=["Au au! Eu sou o Teo, o spitz mais rápido da vila. Você está atrasada, Bela?",
                 "O banquete do castelo começa ao pôr do sol! O caminho mais curto passa pelo bosque escuro, depois pelo vale e pela montanha."],
          after=["A Lana foi para a trilha do norte. Corre! Au!"])
    m.obj(kind="npc", tile=(15, 30), name="Jhonny", sprite="jhonny",
          lines=["Au! Eu sou o Jhonny. Minha irmã Lola é capitã da guarda lá no castelo.",
                 "Ela disse que um dragão enorme dormiu bem na frente do portão. Dragão dorminhoco, imagina!"])
    m.obj(kind="npc", tile=(16, 33), name="Tia Dani", sprite="tia_dani", anim=True,
          lines=["Uma... duas... três... Oi, Bela! Eu sou a Tia Dani. Treino todo dia, até no escuro!",
                 "Quem fortalece o corpo fortalece a coragem. Boa viagem até o castelo!"],
          after=["Já bebeu água hoje? Hidratação é tudo!"])
    m.obj(kind="npc", tile=(18, 33), name="Tio Vitor", sprite="tio_vitor", anim=True,
          lines=["Hnnng... quarenta e oito... quarenta e nove... Ah, oi, Bela! Sou o Tio Vitor.",
                 "Se tiver pedra no caminho, me chama que eu levanto!"],
          after=["Cinquenta! Recorde do dia!"])
    m.obj(kind="npc", tile=(6, 31), name="Tia Evelyn", sprite="evelyn",
          lines=["Konnichiwa, Bela! Eu sou a Tia Evelyn. Chegou uma encomenda da Shopee para você!",
                 "É um presente para o banquete. Eu levo para o castelo, assim você não carrega peso na viagem."],
          after=["Te vejo no jantar! Mata ne!"])
    m.obj(kind="npc", tile=(7, 33), name="Tio William", sprite="william",
          lines=["Eu sou o Tio William, o médico da vila. Deixa eu ver... pulso firme, olhar decidido.",
                 "Você está prontinha para a aventura. Só não esqueça de comer bem no banquete!"],
          after=["Receita do doutor: coragem e um lanche de vez em quando."])
    # enfeites
    for x, y in ((9, 27), (14, 36), (19, 30)):
        m.deco("animal", x, y)
    for x, y in m.free((14, 2, 48, 36), n=16):
        m.deco("firefly", x, y)
    for x, y in ((40, 6), (47, 4), (39, 8), (53, 6)):
        m.deco("firefly", x, y)
    m.save("bosque", "Bosque dos Sussurros")


# =========================================================================== Mundo 2
def vale():
    m = Map(46, 64, seed=202)
    m.rect(0, 0, 45, 63, "#")
    m.rect(2, 2, 17, 30, "g")                        # prado da margem oeste
    m.rect(18, 0, 28, 31, "~")                       # rio largo e calmo
    m.rect(17, 31, 29, 52, "v")                      # corredeiras
    m.rect(14, 31, 16, 52, "W"); m.rect(30, 31, 32, 52, "W")    # paredoes do canion
    m.rect(17, 52, 30, 59, "~")                      # remanso no fim
    m.rect(31, 52, 43, 61, "g")                      # prado do leste
    m.rect(29, 55, 31, 56, "k")                      # cais de chegada
    m.rect(31, 55, 44, 56, "d"); m.rect(44, 55, 45, 56, "G")
    m.rect(4, 6, 15, 7, "d"); m.rect(14, 7, 15, 15, "d")        # trilhas do prado
    m.rect(3, 6, 4, 26, "d"); m.rect(4, 25, 13, 26, "d")
    m.rect(16, 15, 17, 16, "k")                      # cais da Lara
    for x in (19, 22, 25, 28):
        m.g[11][x] = "p"                             # pilares da ponte que sumiu
    m.rect(16, 11, 17, 11, "k")
    m.rect(6, 12, 9, 14, "f"); m.rect(10, 20, 12, 22, "f"); m.rect(34, 58, 37, 60, "f")
    m.rect(5, 16, 9, 19, "h"); m.rect(38, 52, 42, 54, "h")
    for x, y in ((21, 35), (25, 37), (19, 40), (27, 42), (23, 44), (18, 47), (26, 48), (22, 50), (28, 39), (20, 43)):
        m.g[y][x] = "r"                              # pedras nas corredeiras
    for box in ((2, 2, 17, 30), (31, 52, 43, 61)):
        m.reserve(*box)
    m.scatter("r", 6, (2, 2, 13, 29))
    m.obj(kind="npc", tile=(9, 6), name="Rui", sprite="rui",
          lines=["Eu sou o Rui, barqueiro. A ponte velha? A enchente levou embora!",
                 "Só sobraram os pilares. Para descer o vale agora, só de barco, pelas corredeiras.",
                 "A Lara está no cais. Ela é ótima para construir coisas!"],
          after=["Na neblina das corredeiras, a luz da sua lanterna vai mostrar as pedras."])
    m.obj(kind="npc", tile=(15, 16), name="Lara", sprite="lara_chuva", joins="lara", gives="boat",
          requires=["tabuas", "blocos", "vela"],
          missing=["Bela! Lana! Eu sou a Lara. A ponte sumiu, mas eu sei construir um barco!",
                   "Preciso de três coisas: as tábuas velhas, a caixa de blocos de montar e um pano para a vela.",
                   "Está tudo espalhado pelo prado. Vocês me ajudam a achar?"],
          lines=["Tábuas, blocos e a vela! Agora é comigo.",
                 "Lara martela, encaixa os blocos coloridos e prende o mastro... Prontinho!",
                 "Lana: \"Eu amarro as velas!\"  Lara: \"E eu conserto o casco se bater em alguma pedra.\"",
                 "Entre na água pelo cais e o barco leva vocês. Cuidado com a neblina nas corredeiras!"],
          after=["Tudo a bordo! Desçam o rio até o cais lá embaixo."])
    m.obj(kind="pickup", tile=(4, 20), name="Tábuas", item="tabuas",
          lines=["Bela encontrou as tábuas velhas da ponte. Elas ainda servem!"])
    m.obj(kind="pickup", tile=(11, 3), name="Blocos", item="blocos",
          lines=["Uma caixa de blocos de montar coloridos! Perfeitos para o barco."])
    m.obj(kind="pickup", tile=(12, 28), name="Pano da vela", item="vela",
          lines=["Um pano grande, branco e rosa, preso num galho. Vai virar a vela!"])
    sign(m, 6, 4, "Vale dos Córregos. Cuidado: o rio desce forte depois da curva.")
    sign(m, 13, 13, "Ponte do Vale. Interditada depois da enchente.")
    sign(m, 33, 54, "Fim das corredeiras! A estrada leva à Montanha dos Ventos.")
    for x, y in ((7, 9), (12, 18), (6, 27), (36, 57), (40, 59)):
        m.deco("animal", x, y)
    for x, y in ((10, 10), (5, 23), (16, 24), (34, 53), (41, 58)):
        m.deco("bird", x, y)
    for x, y in ((20, 5), (24, 9), (27, 20), (21, 24), (20, 56), (26, 57)):
        m.deco("fish", x, y)
    m.deco("rainbow", 8, 3)
    m.save("vale", "Vale dos Corregos")


# =========================================================================== Mundo 3
def montanha():
    m = Map(48, 34, seed=303)
    m.rect(0, 0, 47, 13, "W")                        # paredao da montanha
    m.rect(2, 14, 45, 31, "g")
    m.rect(8, 2, 9, 13, "w")                         # trilha de vento (subida a pe)
    m.rect(7, 13, 10, 14, "w")
    m.rect(2, 26, 12, 27, "d"); m.rect(11, 20, 12, 27, "d")      # chegada do vale
    m.rect(5, 18, 44, 18, "=")                       # trilhos
    m.rect(44, 2, 44, 18, "=")                       # sobem a montanha ate o castelo
    m.rect(43, 0, 45, 1, "W")
    m.rect(12, 19, 38, 21, "k")                      # plataforma da estacao
    m.rect(7, 15, 10, 17, "d")
    m.rect(26, 10, 31, 13, "W"); m.rect(27, 8, 30, 9, "g")      # rochedo com a arvore dos galhos altos
    m.g[8][27] = m.g[8][28] = m.g[9][27] = m.g[9][28] = "#"
    m.rect(14, 23, 18, 25, "f"); m.rect(30, 24, 34, 26, "f")
    m.rect(36, 26, 42, 29, "h")
    for x, y in ((4, 15), (19, 14), (35, 15), (40, 14), (3, 22), (20, 29), (44, 24), (15, 30)):
        m.g[y][x] = "r"
    m.obj(kind="prop", tile=(18, 16), size=[5, 3], name="Maria Fumaça", image="maria_fumaca", image_w=160,
          steps=[dict(needs=["lara"], sets="canos",
                      lines=["Lara pega as ferramentas: aperta os parafusos e conserta os canos de vapor.",
                             "Lara: \"Pssss... Agora o vapor não vaza mais!\""],
                      missing=["Os canos de vapor estão soltos. Quem sabe consertar?"]),
                 dict(needs=["lenha"], sets="fogo",
                      lines=["Bela coloca a lenha na fornalha e aproxima a Lanterna do Coração, com cuidado.",
                             "O calor da lanterna acende o fogo. A caldeira começa a esquentar!"],
                      missing=["A fornalha está vazia. Precisa de lenha antes de acender."]),
                 dict(needs=[], sets="",
                      lines=["A Maria Fumaça está pronta. Falta só a Olívia dar o sinal!"],
                      missing=[])])
    m.obj(kind="task", tile=(28, 13), name="Galhos altos",
          steps=[dict(needs=["lana"], sets="lenha",
                      lines=["Lá no alto do rochedo há uma árvore com galhos secos.",
                             "Lana escala as pedras como uma cabrita e joga a lenha lá de cima. Tum, tum, tum!",
                             "Bela recolhe a lenha para a fornalha."],
                      missing=["Os galhos secos estão no alto do rochedo. Só uma boa escaladora chega lá."])])
    m.obj(kind="npc", tile=(24, 20), name="Olívia", sprite="olivia_vento", joins="olivia",
          requires=["canos", "fogo"], cutscene="train",
          missing=["Oi, meninas! Eu sou a Olívia. O vento não deixa ninguém subir a montanha a pé...",
                   "Mas esta Maria Fumaça sobe os trilhos até o castelo! Só que ela está parada.",
                   "Precisamos consertar os canos de vapor, buscar lenha nos galhos altos e acender a fornalha.",
                   "Quando estiver tudo pronto, eu toco minha flauta junto com o apito. Eu vou com vocês!"],
          lines=["Canos consertados e fornalha acesa! Agora é a minha vez.",
                 "Olívia toca a flauta... e a Maria Fumaça responde com o grande apito: \"Piiii-uíí!\"",
                 "Todas a bordo!"])
    m.obj(kind="npc", tile=(34, 20), name="Bruce", sprite="bruce",
          lines=["Au! Eu sou o Bruce, chefe da estação. Esta Maria Fumaça é a mais charmosa do reino!",
                 "Ela é velhinha e pesada. Para andar, precisa de ajuda de todo mundo."],
          after=["Piiii-uíí! Adoro esse apito. Au!"])
    sign(m, 7, 16, "Trilha da Montanha. Perigo: ventos fortes! Use o trem.")
    sign(m, 14, 26, "Estação da Montanha dos Ventos. Destino: Castelo.")
    for x, y in ((6, 23), (22, 28), (40, 22)):
        m.deco("animal", x, y)
    for x, y in ((16, 15), (31, 16), (38, 23), (27, 27)):
        m.deco("bird", x, y)
    m.save("montanha", "Montanha dos Ventos")


# =========================================================================== Final
def castelo():
    m = Map(32, 24, seed=404)
    m.rect(0, 0, 31, 1, "#")
    m.rect(0, 2, 31, 5, "K")                         # muralha
    m.rect(14, 3, 17, 5, "C")                        # portao
    m.rect(2, 6, 29, 21, "g")
    m.rect(12, 6, 19, 18, "s")                       # patio de pedra
    m.rect(14, 18, 17, 22, "d")
    m.rect(14, 22, 17, 23, "k")                      # chegada do trem (plataforma)
    m.rect(4, 8, 8, 10, "f"); m.rect(23, 8, 27, 10, "f"); m.rect(4, 15, 7, 17, "f"); m.rect(24, 15, 27, 17, "f")
    for x, y in ((10, 7), (21, 7), (10, 16), (21, 16)):
        m.g[y][x] = "L"
    m.obj(kind="prop", tile=(13, 6), size=[6, 4], name="Dragão Sonolento", image="dragon_sleep", image_w=192,
          snore=True, cutscene="final",
          steps=[dict(needs=["lana"], sets="pena",
                      lines=["Lana tira uma pena do cabelo e faz cócegas no nariz do dragão.",
                             "Dragão: \"Atchim... Rrrrr...\" Ele se mexe, mas continua dormindo."],
                      missing=["Um dragão imenso, escamoso e fofo dorme na frente do portão. Ronc... ronc..."]),
                 dict(needs=["lara"], sets="rampa",
                      lines=["Lara monta uma rampa de tábuas e blocos ao lado do rabo do dragão.",
                             "O rabo escorrega devagarinho pela rampa e sai do caminho. Ploft!"],
                      missing=["O rabo enorme do dragão continua no caminho."]),
                 dict(needs=["olivia"], sets="ninar",
                      lines=["Olívia toca uma canção de ninar bem calminha na flauta.",
                             "O dragão sorri dormindo e solta um suspiro de nuvenzinhas cor-de-rosa."],
                      missing=["Talvez uma música ajude..."]),
                 dict(needs=[], sets="quentinho",
                      lines=["Bela levanta a Lanterna do Coração e cria um cantinho quentinho ao lado do portão.",
                             "O dragão sente o calor gostoso e rola devagar para lá..."],
                      missing=[])])
    m.obj(kind="npc", tile=(9, 12), name="Lola", sprite="lola",
          lines=["Au! Eu sou a Lola, capitã da guarda do castelo. Vocês chegaram bem na hora!",
                 "Este dragão chegou à tarde, deitou na frente do portão e dormiu. Ninguém consegue passar!",
                 "Com jeitinho e as quatro juntas, aposto que ele sai. Falem com ele!"],
          after=["O banquete já está servido lá dentro. Só falta o dragão sair do caminho!"])
    sign(m, 18, 20, "Castelo Real. Hoje: Grande Banquete ao pôr do sol!")
    for x, y in ((6, 12), (25, 12), (5, 19), (26, 19)):
        m.deco("bird", x, y)
    m.save("castelo", "Portao do Castelo")


if __name__ == "__main__":
    bosque()
    vale()
    montanha()
    castelo()
