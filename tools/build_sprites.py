#!/usr/bin/env python3
"""Converte art/src/<nome>.sprite.txt em assets/sprites/<nome>.png (quadros lado a lado)
e uma previa ampliada 8x em art/preview/. Paleta: tabela de 32 cores do DESIGN.md.
Uso: python3 tools/build_sprites.py [nome ...]   (sem nomes: todos os .sprite.txt)
"""
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
import pygame  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC, OUT, PREVIEW = ROOT / "art" / "src", ROOT / "assets" / "sprites", ROOT / "art" / "preview"
SCALE = 8


def palette():
    pal = {}
    for line in (ROOT / "DESIGN.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| `(.)` \| \w+ \| `#([0-9A-Fa-f]{6})`", line)
        if m:
            pal[m.group(1)] = tuple(int(m.group(2)[i:i + 2], 16) for i in (0, 2, 4))
    return pal


def frames_of(path):
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if not l.startswith("#")]
    frames, cur = [], []
    for line in lines:
        if line == "---":
            frames.append(cur)
            cur = []
        elif line:
            cur.append(line)
    frames.append(cur)
    return frames


def build(path, pal):
    frames = frames_of(path)
    fw, fh = len(frames[0][0]), len(frames[0])
    sheet = pygame.Surface((fw * len(frames), fh), pygame.SRCALPHA)
    for i, fr in enumerate(frames):
        for y, row in enumerate(fr):
            for x, ch in enumerate(row):
                if ch != ".":
                    sheet.set_at((i * fw + x, y), (*pal[ch], 255))
    name = path.name[: -len(".sprite.txt")]
    pygame.image.save(sheet, str(OUT / f"{name}.png"))
    big = pygame.transform.scale(sheet, (sheet.get_width() * SCALE, sheet.get_height() * SCALE))
    pygame.image.save(big, str(PREVIEW / f"{name}.png"))
    return name


def main():
    pal = palette()
    names = sys.argv[1:]
    paths = sorted(SRC.glob("*.sprite.txt"))
    if names:
        paths = [p for p in paths if any(p.name.startswith(n + "_") or p.name == n + ".sprite.txt" for n in names)]
    for p in paths:
        print("png:", build(p, pal))


if __name__ == "__main__":
    main()
