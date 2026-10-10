#!/usr/bin/env bash
# Empacota o jogo para a web com pygbag. Saida: dist/web/ (index.html + arquivos do jogo)
# Cada build recebe um nome versionado (bela_AAAAMMDDHHMM): o navegador nunca reaproveita
# um pacote antigo do cache. Uso: tools/build_web.sh   (requer: pip install pygbag)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VERSION="bela_$(date +%Y%m%d%H%M)"
STAGE="$(mktemp -d)/$VERSION"
mkdir -p "$STAGE"
cp "$ROOT/main.py" "$STAGE/"
cp -R "$ROOT/src" "$ROOT/assets" "$STAGE/"
find "$STAGE" -name __pycache__ -type d -prune -exec rm -rf {} +
python3 -m pygbag --build "$STAGE"
# pagina cheia: o pygbag usa so metade da largura (gui_divider 2) e escala suavizado; ajusta
python3 - "$STAGE/build/web/index.html" <<'PYEOF'
import re, sys
p = sys.argv[1]
t = open(p, encoding="utf-8").read()
t = t.replace("gui_divider : 2,", "gui_divider : 1,")
t = t.replace("canvas.emscripten {\n            border: 0px none;",
              "canvas.emscripten {\n            image-rendering: pixelated;\n            border: 0px none;")
open(p, "w", encoding="utf-8").write(t)
print("index.html ajustado: pagina cheia e escala nitida")
PYEOF
rm -rf "$ROOT/dist/web"
mkdir -p "$ROOT/dist"
cp -R "$STAGE/build/web" "$ROOT/dist/web"
echo "Pronto: $ROOT/dist/web  (versao $VERSION)"
