# A Jornada da Bela

Jogo de aventura em pixel art vista de cima (estilo GBA), feito em **Python + Pygame** e
publicado no navegador com **pygbag** (WebAssembly).

A Princesa Isabela ("Bela") e as melhores amigas (Lana, Lara e Olívia) atravessam o Bosque dos
Sussurros, o Vale dos Córregos e a Montanha dos Ventos para chegar ao castelo a tempo do jantar,
com um unicórnio, um barco de blocos de montar, uma Maria Fumaça e um dragão dorminhoco. Veja `STORY.md`.

**Estado:** história completa jogável, em 640x360: abertura, os quatro mundos, a viagem de trem e
o final com o banquete.

## Controles

| Ação | Teclado | Toque |
|---|---|---|
| Mover | setas ou WASD | direcional |
| Interagir / pular (unicórnio) | Z, Espaço ou Enter | botão A |
| Mochila (transportes, amigas, itens) | I ou Tab | botão I |
| Pausa | Esc ou P | botão \|\| |

## Rodar localmente

```bash
pip install pygame
python main.py
```

## Build para a web

```bash
pip install pygbag
tools/build_web.sh        # gera dist/web/
```

Sirva `dist/web/` com qualquer servidor estático. Para publicar num servidor próprio,
use `tools/deploy_homolog.sh` com as variáveis `BELA_DEPLOY_HOST` e `BELA_DEPLOY_KEY`.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `src/` | código do jogo (estados, mundo, entidades, UI, toque) |
| `assets/` | mapas (`.map.txt`, `.json`) e sprites PNG gerados |
| `art/src/` | fontes da arte (grades de caracteres, paleta de 32 cores) |
| `tools/` | geradores de arte e do mapa, build e deploy |
| `DESIGN.md` | decisões de projeto |
| `STORY.md` | enredo, roupas por fase e personagens |

A arte é gerada por código a partir de uma paleta fixa de 32 cores: `tools/gen_characters.py`
(meninas e roupas por fase), `tools/gen_dogs.py`, `tools/gen_gym.py`, `tools/gen_critters.py`,
`tools/gen_vehicles.py`, `tools/gen_props.py` (Maria Fumaça e dragão), `src/world/tileart.py`
(terreno) e `src/scenery.py` (paisagem). `tools/build_sprites.py` converte as grades de texto em
PNG, ampliando 2x (`tools/pixel.py`). Os mapas saem de `tools/gen_world.py`.

## Créditos

- Fonte **Jersey 15** (SIL Open Font License 1.1), em `assets/fonts/`.
