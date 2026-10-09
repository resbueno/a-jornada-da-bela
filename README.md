# A Jornada da Bela

Jogo de aventura em pixel art vista de cima (estilo GBA), feito em **Python + Pygame** e
publicado no navegador com **pygbag** (WebAssembly).

A Princesa Isabela ("Bela") precisa reunir os Quatro Insumos Ancestrais (barco, unicórnio,
carro rosa e dragão) para libertar o castelo da Sombra Cinzenta. Veja `STORY.md`.

**Estado:** capítulos 1 (floresta) e 2 (lago e ilha) jogáveis; capítulo 3 em construção.

## Controles

| Ação | Teclado | Toque |
|---|---|---|
| Mover | setas ou WASD | direcional |
| Interagir / saltar (unicórnio) | Z, Espaço ou Enter | botão A |
| Inventário (trocar transporte) | I ou Tab | botão I |
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
| `STORY.md` | enredo e personagens |

A arte é gerada por código (`tools/gen_characters.py`, `tools/gen_vehicles.py`,
`src/world/tileart.py`) a partir de uma paleta fixa de 32 cores.
