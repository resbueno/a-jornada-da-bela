#!/usr/bin/env python3
"""Converte art/src/<nome>.sprite.txt em assets/sprites/<nome>.png (quadros lado a lado)
e uma previa ampliada 4x em art/preview/. Paleta: tabela de 32 cores do DESIGN.md.

Arte marcada com `@hd` no cabecalho ja esta na resolucao final. O resto (grade base, 16 px)
passa pelo `pixel.hd`: 2x com EPX, contorno fino, sombra e brilho.
Uso: python3 tools/build_sprites.py [nome ...]   (sem nomes: todos os .sprite.txt)
"""
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame  # noqa: E402

import pixel  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT, PREVIEW = ROOT / "art" / "src", ROOT / "assets" / "sprites", ROOT / "art" / "preview"
SCALE = 4


def palette():
    pal = {}
    for line in (ROOT / "DESIGN.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| `(.)` \| \w+ \| `#([0-9A-Fa-f]{6})`", line)
        if m:
            pal[m.group(1)] = tuple(int(m.group(2)[i:i + 2], 16) for i in (0, 2, 4))
    return pal


def upscale(lines):
    """Grade base -> 2x: o contorno externo (`r` encostado no vazio) vira `R` antes do hd."""
    g = pixel.Grid.from_lines(lines)
    src = [row[:] for row in g.g]
    for y in range(g.h):
        for x in range(g.w):
            if src[y][x] != "r":
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < g.w and 0 <= ny < g.h) or src[ny][nx] == pixel.CLEAR:
                    g.g[y][x] = pixel.OUTLINE
                    break
    return pixel.hd(g, skip=("j", "k")).lines()


def build(path, pal):
    head, frames = pixel.read_frames(path)
    if not any("@hd" in h for h in head):
        frames = [upscale(fr) for fr in frames]
    fw, fh = len(frames[0][0]), len(frames[0])
    sheet = pygame.Surface((fw * len(frames), fh), pygame.SRCALPHA)
    for i, fr in enumerate(frames):
        for y, row in enumerate(fr):
            for x, ch in enumerate(row):
                if ch != pixel.CLEAR:
                    sheet.set_at((i * fw + x, y), (*pal[ch], 255))
    name = path.name[: -len(".sprite.txt")]
    OUT.mkdir(parents=True, exist_ok=True)
    PREVIEW.mkdir(parents=True, exist_ok=True)
    pygame.image.save(sheet, str(OUT / f"{name}.png"))
    big = pygame.transform.scale(sheet, (sheet.get_width() * SCALE, sheet.get_height() * SCALE))
    pygame.image.save(big, str(PREVIEW / f"{name}.png"))
    return name


def main():
    pal = palette()
    names = sys.argv[1:]
    paths = sorted(SRC.glob("*.sprite.txt"))
    if names:
        paths = [p for p in paths if p.name[: -len(".sprite.txt")] in names
                 or any(p.name.startswith(n + "_") for n in names)]
    for p in paths:
        print("png:", build(p, pal))


if __name__ == "__main__":
    main()
