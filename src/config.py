"""Constantes do jogo. Fonte unica de resolucao, tile, tempo e paleta (ver DESIGN.md)."""

TITLE = "A Jornada da Bela"

# Resolucao logica e tiles
LOGICAL_W = 320
LOGICAL_H = 180
TILE = 16

# Janela inicial: escala inteira 3x (960x540)
START_SCALE = 3

# Tempo: passo fixo de logica
UPDATE_HZ = 60
DT = 1.0 / UPDATE_HZ
MAX_FRAME_TIME = 0.25  # evita espiral de atualizacoes apos travadas

# Clima do mapa inicial: "rain" ou "none"
WEATHER = "rain"

# Toque: True mostra os controles sempre (senao: ao primeiro toque ou em janela em pe)
TOUCH_ALWAYS = False

# Depuracao
DEBUG_HITBOX = False
# True libera todos os transportes de cara (so para testes). No jogo, os NPCs entregam.
DEBUG_UNLOCK_ALL_TRANSPORTS = False


def _hex(value):
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


# Paleta de 32 cores (mesma de palette.json da skill pixelart-sprites), nomeada por papel
PALETTE = {
    "verde_contorno": _hex("#1F3A0E"),
    "verde_escuro": _hex("#2D5D14"),
    "verde_medio": _hex("#3E8E31"),
    "verde_claro": _hex("#83CE60"),
    "verde_brilho": _hex("#B3F98D"),
    "chao_sombra": _hex("#44AD7D"),
    "chao": _hex("#71C7A2"),
    "chao_claro": _hex("#9DE2BD"),
    "areia_sombra": _hex("#A8985A"),
    "areia": _hex("#CFC07D"),
    "areia_clara": _hex("#E8DDA8"),
    "rocha_contorno": _hex("#4A3030"),
    "rocha": _hex("#7D5C5C"),
    "rocha_clara": _hex("#B09090"),
    "madeira_escura": _hex("#624634"),
    "madeira": _hex("#9A7048"),
    "agua_escura": _hex("#2A5FA8"),
    "agua": _hex("#4A8FD8"),
    "agua_clara": _hex("#A8D8F0"),
    "pele": _hex("#F8D8B0"),
    "pele_sombra": _hex("#D89870"),
    "vermelho": _hex("#E04030"),
    "vermelho_escuro": _hex("#A02020"),
    "branco": _hex("#FFFFFF"),
    "amarelo": _hex("#F8C830"),
    "laranja": _hex("#E88830"),
    "azul": _hex("#3858A8"),
    "contorno": _hex("#181830"),
    "roxo": _hex("#8858C8"),
    "rosa": _hex("#F8A0C8"),
    "rosa_escuro": _hex("#C06090"),
    "ceu": _hex("#58B8F8"),
}

# Nomes antigos (paleta de 16 cores) apontando para o tom mais proximo
PALETTE["contorno_antigo"] = PALETTE["contorno"]
PALETTE["sombra_caverna"] = PALETTE["rocha_contorno"]
PALETTE["pedra_escura"] = PALETTE["rocha"]
PALETTE["pedra_clara"] = PALETTE["rocha_clara"]
PALETTE["folha_escura"] = PALETTE["verde_escuro"]
PALETTE["grama"] = PALETTE["chao"]
PALETTE["luz_folhagem"] = PALETTE["verde_claro"]
PALETTE["tronco_terra"] = PALETTE["madeira_escura"]
PALETTE["madeira_terra_clara"] = PALETTE["areia"]
PALETTE["agua_lago"] = PALETTE["agua"]
PALETTE["ceu_reflexo"] = PALETTE["ceu"]
PALETTE["creme"] = PALETTE["areia_clara"]
PALETTE["lilas_magia"] = PALETTE["roxo"]
PALETTE["amarelo_brilho"] = PALETTE["amarelo"]
PALETTE["vermelho_vida"] = PALETTE["vermelho"]
