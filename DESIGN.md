# A Jornada da Bela — Design

Jogo de aventura vista de cima (estilo Zelda), pixel art, em Python, jogado no navegador por um link hospedado na VPS do autor.

## Fase 1 — Infraestrutura

| Item | Decisão |
|---|---|
| Biblioteca | Pygame + pygbag (WebAssembly). Loop principal `async`, cede o controle ao navegador a cada frame (`await asyncio.sleep(0)`) |
| Resolução lógica | 320x180 (16:9) |
| Escala | Upscale por fator inteiro, filtro nearest (×4 em 720p, ×6 em 1080p) |
| Tile | 16x16 (20 colunas x 11 linhas + 4 px de sobra na vertical) |
| Timestep | Passo fixo a 60 Hz com acumulador. Posição lógica em float; arredondada para inteiro só ao desenhar |
| Paleta | 32 cores (v2, estilo GBA), definida em `palette.json` da skill `pixelart-sprites` |
| Assets | PNG em spritesheets de grade 16x16, geradas por código (skill `pixelart-sprites`); áudio em `.ogg` |

### Paleta (v2, 32 cores)

Substitui a paleta inicial de 16 cores, que nao dava o nivel de sombreamento da referencia visual.

| Char | Papel | Hex |
|---|---|---|
| `0` | verde_contorno | `#1F3A0E` |
| `1` | verde_escuro | `#2D5D14` |
| `2` | verde_medio | `#3E8E31` |
| `3` | verde_claro | `#83CE60` |
| `4` | verde_brilho | `#B3F98D` |
| `5` | chao_sombra | `#44AD7D` |
| `6` | chao | `#71C7A2` |
| `7` | chao_claro | `#9DE2BD` |
| `8` | areia_sombra | `#A8985A` |
| `9` | areia | `#CFC07D` |
| `a` | areia_clara | `#E8DDA8` |
| `b` | rocha_contorno | `#4A3030` |
| `c` | rocha | `#7D5C5C` |
| `d` | rocha_clara | `#B09090` |
| `e` | madeira_escura | `#624634` |
| `f` | madeira | `#9A7048` |
| `g` | agua_escura | `#2A5FA8` |
| `h` | agua | `#4A8FD8` |
| `i` | agua_clara | `#A8D8F0` |
| `j` | pele | `#F8D8B0` |
| `k` | pele_sombra | `#D89870` |
| `l` | vermelho | `#E04030` |
| `m` | vermelho_escuro | `#A02020` |
| `n` | branco | `#FFFFFF` |
| `o` | amarelo | `#F8C830` |
| `p` | laranja | `#E88830` |
| `q` | azul | `#3858A8` |
| `r` | contorno | `#181830` |
| `s` | roxo | `#8858C8` |
| `t` | rosa | `#F8A0C8` |
| `u` | rosa_escuro | `#C06090` |
| `v` | ceu | `#58B8F8` |

### Estrutura de pastas

```
a-jornada-da-bela/
├── main.py              # ponto de entrada (async, exigido pelo pygbag)
├── src/                 # código do jogo, módulos pequenos e desacoplados
├── assets/
│   ├── sprites/         # PNGs gerados pela skill pixelart-sprites
│   ├── maps/            # mapas das fases
│   └── audio/           # sons e músicas em .ogg
├── art/
│   ├── src/             # *.sprite.txt (fontes da arte)
│   └── preview/         # prévias ampliadas
└── DESIGN.md
```

## Fase 2 — Máquina de estados e mecânicas

### Jogo
Aventura vista de cima, movimento em 4 direções, suave em pixels, sem perigo e sem derrota. Objetivo: chegar ao castelo.

### Câmera
Scroll suave, posição inteira ao desenhar, presa às bordas do mapa (mapas maiores que 320x180).

### Estados do jogo

| De | Evento | Para |
|---|---|---|
| Título | Iniciar | Jogando |
| Jogando | Tecla de pausa | Pausa |
| Jogando | Interagir com NPC ou placa | Diálogo |
| Jogando | Tecla de inventário | Inventário |
| Jogando | Chegar ao castelo | Vitória |
| Pausa | Retomar | Jogando |
| Pausa | Sair | Título |
| Diálogo | Último texto concluído | Jogando |
| Inventário | Escolher transporte compatível com o terreno | Jogando (transporte trocado) |
| Inventário | Escolher transporte incompatível | Permanece, com mensagem de recusa |
| Inventário | Fechar | Jogando |
| Vitória | Continuar | Título |

### Bela
- Estados: parada e andando, nas 4 direções (arte: frente, costas e lado espelhado).
- O transporte atual é um atributo: a pé, unicórnio, barco ou carro rosa.
- Movimento suave em pixels; hitbox pequena, checada contra o tipo de terreno do tile.

### Transportes

A troca é feita pelo inventário e só é aceita em terreno compatível. Cada transporte é obtido conversando com um NPC.

| Transporte | Anda em | Não entra em | Velocidade |
|---|---|---|---|
| A pé | grama, terra, pedra | água funda | normal |
| Unicórnio | grama, terra, pedra | água, caverna estreita | rápida |
| Barco | água | terra firme | média |
| Carro rosa | terra (caminhos) | grama alta, água, caverna | rápida |

### Progressão
Obstáculos naturais (lago largo, estrada longa, mata) exigem o transporte certo. Cada transporte é conseguido com um NPC (diálogo) e entra no inventário. O castelo fica depois do último obstáculo.

### Entidades

| Entidade | O que faz |
|---|---|
| Bela | Anda, interage e carrega o transporte atual |
| NPC | Abre diálogo; pode entregar um transporte |
| Item de transporte | Vai para o inventário |
| Obstáculo | Terreno que só um transporte atravessa |
| Castelo (meta) | Dispara a Vitória |
| Câmera | Scroll suave, presa às bordas do mapa |
| Placa | Ao interagir, abre diálogo com o texto |
| Decorativos | Animais soltos, peixes, aves e arco-íris; reagem à Bela só visualmente (sem colisão, sem efeito na progressão) |

### Controles
- Teclado: setas ou WASD, uma tecla de ação (interagir) e uma de inventário/pausa.
- Toque: direcional e botões virtuais.
- Layout de toque por orientação: celular em pé, controles fora da imagem (abaixo do jogo); celular deitado, controles semitransparentes sobre o jogo, nos cantos.

## Ordem de implementação

A definir na Fase 3 (blueprint).

## Revisão 2 — Enredo adotado (aventura sem derrota)

Decidido em 2026-10-09 com base em `STORY.md`. O tom continua **sem barra de vida e sem
derrota**; o enredo entra como conteúdo.

- **Protagonista:** Princesa Isabela ("Bela"): cabelos longos pretos, pele bronzeada.
- **Ordem dos transportes (4 insumos):** barco (Olívia) → unicórnio (Lara) → carro rosa
  (Lana) → dragão (Sara). Cada um é entregue pela princesa guardiã ao fim do capítulo.
- **Mecânicas novas:** unicórnio **salta** penhascos e fendas (ação de pulo); dragão é o
  último insumo e fecha o clímax.
- **"Perigos" viram desafios sem punição:** tempestade no lago, corrida desviando de
  obstáculos (capítulo 4), abismos que só o unicórnio cruza. Errar recomeça o trecho.
- **Duelo final:** cena roteirizada / momento de timing, sem combate completo.
- **Estrutura:** 4 capítulos em mapas próprios (floresta+vilarejo, lago+ilha, cavernas
  de quartzo, estrada costeira) e os portões do castelo para o clímax.
- **Personagens:** ver `STORY.md`. Cabelo da Lana e visual da Sombra Cinzenta a definir.
- **Arte:** personagens em 16x24 (4 direções via espelho; 3 frames por direção), paleta
  de 32 cores.

## Revisão 3 — Capítulo 2 implementado (Lago de Cristal)

- **Salto do unicórnio:** com o unicórnio montado e de frente para uma **fenda** (`x` no
  mapa), a tecla de interação (A no toque) salta 1 ou 2 tiles de fenda. Durante o salto
  não há controle; o pouso exige terreno livre.
- **Criaturas corrompidas (enguias):** patrulham o lago e **empurram o barco** ao
  encostar. Sem dano e sem derrota; aparece um aviso curto na tela.
- **Tempestade:** enquanto a Isabela está de barco, a chuva fica mais forte e há
  relâmpagos; fora do barco, o tempo é calmo.
- **Ilha da Lara:** a entrada da Caverna de Quartzo (`E`) fica atrás de uma fenda. Pisar
  nela encerra o capítulo 2 (tela de fim de capítulo).
- **Arte:** veículos 32x32 com a Isabela montada (`tools/gen_vehicles.py`), chuva e
  caverna com relevo.

## Revisão 4 — Capítulo 3 implementado (Cavernas de Quartzo)

- **Vários mapas:** `src/maps.py` registra os mapas e as passagens (`CAVE` na ilha leva
  às cavernas; `EXIT` volta à ilha). Inventário e transporte são mantidos na troca.
- **Caverna escura:** `src/lighting.py` escurece a cena e abre halos de luz em degraus ao
  redor da Isabela, dos cristais de quartzo (tremulam) e das NPCs.
- **Abismos:** `x` no mapa. Largura 1 ou 2 tiles; só o unicórnio salta (mesma mecânica
  das fendas do capítulo 2). A pé ou de carro não atravessam.
- **Lana:** entrega o Carro Rosa (3º insumo) na câmara de cristais. O carro só anda em
  trilhas de terra, então não circula dentro da caverna.
- **Fim do capítulo 3:** portal luminoso (`G`) depois da Lana. O capítulo 4 ainda não existe.
- **Novos terrenos:** parede (`W`), cristal (`q`), saída (`O`), portal (`G`).
- **Cartão de capítulo** no começo de cada mapa que o define.
