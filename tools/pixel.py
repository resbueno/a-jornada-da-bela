"""Utilitarios de pixel art compartilhados pelos geradores (grades de caracteres da paleta).

Pipeline de alta resolucao (2x): os geradores desenham na grade base com o contorno marcado como
`R`; `hd()` amplia com EPX (suaviza diagonais), afina o contorno para 1 px e aplica sombra e
brilho nas bordas (luz vindo de cima, a esquerda).
"""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "art" / "src"
CLEAR = "."
OUTLINE = "R"       # contorno provisorio (vira `r` depois do hd)

# tom mais escuro e mais claro de cada cor da paleta (ver DESIGN.md)
DARK = {
    "o": "p", "p": "m", "a": "9", "9": "8", "t": "u", "u": "m", "l": "m", "m": "b",
    "h": "g", "i": "h", "v": "h", "g": "q", "3": "2", "2": "1", "1": "0", "4": "3",
    "f": "e", "e": "b", "n": "i", "s": "q", "q": "r", "c": "b", "d": "c",
    "j": "k", "k": "f", "6": "5", "7": "6", "8": "e",
}
LIGHT = {
    "o": "a", "p": "o", "t": "n", "u": "t", "l": "p", "m": "l", "h": "i", "g": "h",
    "2": "3", "1": "2", "3": "4", "e": "f", "f": "9", "s": "t", "q": "h", "c": "d",
    "d": "n", "r": "q", "b": "c", "9": "a", "i": "n", "v": "i", "5": "6", "6": "7",
}


class Grid:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.g = [[CLEAR] * w for _ in range(h)]

    @classmethod
    def from_lines(cls, lines):
        grid = cls(len(lines[0]), len(lines))
        grid.g = [list(row) for row in lines]
        return grid

    def get(self, x, y):
        return self.g[y][x] if 0 <= x < self.w and 0 <= y < self.h else CLEAR

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            self.g[y][x] = c

    def rect(self, x0, y0, x1, y1, c):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.px(x, y, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                    self.px(x, y, c)

    def line(self, x0, y0, x1, y1, c, width=1):
        n = max(abs(x1 - x0), abs(y1 - y0), 1)
        for i in range(n + 1):
            x = round(x0 + (x1 - x0) * i / n)
            y = round(y0 + (y1 - y0) * i / n)
            self.rect(x - width // 2, y - width // 2, x + (width - 1) // 2, y + (width - 1) // 2, c)

    def outline(self, color=OUTLINE):
        """Contorno de 1 px em volta de tudo que foi pintado."""
        src = [row[:] for row in self.g]
        for y in range(self.h):
            for x in range(self.w):
                if src[y][x] != CLEAR:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.w and 0 <= ny < self.h and src[ny][nx] != CLEAR:
                        self.g[y][x] = color
                        break

    def flip(self):
        out = Grid(self.w, self.h)
        out.g = [row[::-1] for row in self.g]
        return out

    def lines(self):
        return ["".join(r) for r in self.g]


def epx(grid):
    """Scale2x/EPX: dobra a grade suavizando as diagonais (bom para pixel art)."""
    out = Grid(grid.w * 2, grid.h * 2)
    for y in range(grid.h):
        for x in range(grid.w):
            p = grid.g[y][x]
            a, b, c, d = grid.get(x, y - 1), grid.get(x + 1, y), grid.get(x - 1, y), grid.get(x, y + 1)
            e1 = e2 = e3 = e4 = p
            if c == a and c != d and a != b:
                e1 = a
            if a == b and a != c and b != d:
                e2 = b
            if d == c and d != b and c != a:
                e3 = c
            if b == d and b != a and d != c:
                e4 = d
            out.g[2 * y][2 * x], out.g[2 * y][2 * x + 1] = e1, e2
            out.g[2 * y + 1][2 * x], out.g[2 * y + 1][2 * x + 1] = e3, e4
    return out


def thin_outline(grid, color="r"):
    """Contorno `R` com 2 px (depois do EPX) vira 1 px: a parte de dentro assume a cor vizinha."""
    src = [row[:] for row in grid.g]

    def outer(x, y):
        return any(not (0 <= x + dx < grid.w and 0 <= y + dy < grid.h) or src[y + dy][x + dx] == CLEAR
                   for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))

    for y in range(grid.h):
        for x in range(grid.w):
            if src[y][x] != OUTLINE:
                continue
            if outer(x, y):
                grid.g[y][x] = color
                continue
            fill = None
            for dx, dy in ((0, -1), (-1, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)):
                c = grid.get(x + dx, y + dy)
                if c not in (CLEAR, OUTLINE):
                    fill = c
                    break
            grid.g[y][x] = DARK.get(fill, fill) if fill else color
    return grid


def shade(grid, outline="r", skip=()):
    """Sombra nas bordas de baixo/direita e brilho nas de cima/esquerda (cores em `skip` ficam iguais)."""
    src = [row[:] for row in grid.g]

    def edge(x, y):
        c = src[y][x] if 0 <= x < grid.w and 0 <= y < grid.h else CLEAR
        return c in (CLEAR, outline)

    for y in range(grid.h):
        for x in range(grid.w):
            c = src[y][x]
            if c in (CLEAR, outline) or c in skip:
                continue
            if edge(x + 1, y) or edge(x, y + 1):
                grid.g[y][x] = DARK.get(c, c)
            elif (edge(x - 1, y) or edge(x, y - 1)) and c in LIGHT:
                grid.g[y][x] = LIGHT[c]
    return grid


def hd(grid, skip=()):
    """Grade base com contorno `R` -> grade 2x com contorno fino, sombra e brilho."""
    big = thin_outline(epx(grid))
    return shade(big, skip=skip)


def read_frames(path):
    """Quadros de um .sprite.txt (separados por ---). Devolve (cabecalho, [linhas])."""
    text = Path(path).read_text(encoding="utf-8").splitlines()
    head = [l for l in text if l.startswith("#")]
    frames, cur = [], []
    for line in text:
        if line.startswith("#"):
            continue
        if line == "---":
            frames.append(cur)
            cur = []
        elif line:
            cur.append(line)
    frames.append(cur)
    return head, frames


def save(name, frames, note, hd_ready=True):
    """Grava art/src/<name>.sprite.txt; `@hd` marca arte ja na resolucao final."""
    OUT.mkdir(parents=True, exist_ok=True)
    body = "\n---\n".join("\n".join(fr.lines() if isinstance(fr, Grid) else fr) for fr in frames)
    tag = " @hd" if hd_ready else ""
    (OUT / f"{name}.sprite.txt").write_text(f"# {note}{tag}\n{body}\n", encoding="utf-8")
