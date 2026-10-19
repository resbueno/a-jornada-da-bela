"""Registro dos mapas da jornada, na ordem: bosque -> vale -> montanha -> castelo.

Cada mapa define a roupa da fase (`outfit`: sufixo dos sprites das meninas), o estilo do chao,
clima, escuridao/neblina, a hora do dia (o sol vai baixando ate o jantar), o objetivo mostrado
na tela e a proxima parada.
"""

MAPS = {
    "bosque": dict(
        base="assets/maps/bosque", spawn=(12, 34), style="bosque", outfit="bosque",
        weather=None, dark=True, tint="tarde", hour=0.25, transports=("unicorn",), next="vale",
        card="Mundo 1: O Bosque dos Sussurros",
        goals=[("lana", "Encontre a Lana na trilha do norte"),
               ("espinho1", "Tire os espinheiros do caminho com a Lana"),
               ("espinho2", "Siga a trilha e tire mais espinheiros"),
               ("unicorn", "Acalme o unicórnio perdido com a lanterna"),
               ("", "Pule o desfiladeiro com o unicórnio (A)")]),
    "vale": dict(
        base="assets/maps/vale", spawn=(5, 4), style="vale", outfit="chuva",
        weather="rain", fog=True, tint="tarde", hour=0.5, transports=("boat",), next="montanha",
        card="Mundo 2: O Vale dos Córregos",
        intro=["O unicórnio voltou feliz para o bosque. Tchau, unicórnio!",
               "Aqui no vale chove bastante. Ainda bem que as meninas trouxeram capa de chuva!"],
        goals=[("falou_lara", "Encontre a Lara perto do cais"),
               ("tabuas", "Ache as tábuas velhas no prado"),
               ("blocos", "Ache a caixa de blocos de montar"),
               ("vela", "Ache um pano para a vela"),
               ("boat", "Leve tudo para a Lara construir o barco"),
               ("", "Desça as corredeiras até o cais lá embaixo")]),
    "montanha": dict(
        base="assets/maps/montanha", spawn=(3, 26), style="montanha", outfit="vento",
        weather="wind", tint="entardecer", hour=0.75, transports=(), next="castelo",
        card="Mundo 3: A Montanha dos Ventos",
        intro=["Que vento! As meninas vestem os casacos, os gorros e os cachecóis.",
               "Lá no alto da montanha fica o castelo. Como subir com esse vento todo?"],
        goals=[("falou_olivia", "Fale com a menina perto da Maria Fumaça"),
               ("canos", "Conserte os canos de vapor (Lara)"),
               ("lenha", "Busque lenha nos galhos altos (Lana)"),
               ("fogo", "Acenda a fornalha com a lanterna"),
               ("", "Fale com a Olívia para dar a partida")]),
    "castelo": dict(
        base="assets/maps/castelo", spawn=(15, 21), style="castelo", outfit="gala",
        weather=None, tint="por_do_sol", hour=0.95, transports=(), next=None,
        card="O Grande Final: O Portão do Castelo",
        intro=["Chegamos! As meninas trocam a roupa de viagem pelos vestidos do banquete.",
               "Mas... quem é aquele dorminhoco enorme na frente do portão?"],
        goals=[("pena", "Acorde o nariz do dragão (Lana)"),
               ("rampa", "Tire o rabo do dragão do caminho (Lara)"),
               ("ninar", "Uma canção de ninar (Olívia)"),
               ("", "Faça um cantinho quentinho com a lanterna")]),
}

ORDER = ["bosque", "vale", "montanha", "castelo"]


def sprite_for(name, map_id):
    """Sprite da menina com a roupa da fase (ex.: lana + vale -> lana_chuva), se existir."""
    from src.world.tilemap import ROOT

    outfit = MAPS[map_id]["outfit"]
    cand = f"{name}_{outfit}"
    if (ROOT / "assets" / "sprites" / f"{cand}_down.png").exists():
        return cand
    return name
