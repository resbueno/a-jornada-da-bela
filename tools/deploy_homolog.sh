#!/usr/bin/env bash
# Publica dist/web numa pasta /root/bela/site de um servidor via SSH/SCP.
# Variaveis: BELA_DEPLOY_HOST (ex.: root@meu.servidor) e BELA_DEPLOY_KEY (chave privada SSH).
# Pre-requisito: tools/build_web.sh. So troca os arquivos estaticos.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOST="${BELA_DEPLOY_HOST:?defina BELA_DEPLOY_HOST (ex.: root@meu.servidor)}"
KEY="${BELA_DEPLOY_KEY:?defina BELA_DEPLOY_KEY (caminho da chave SSH)}"
URL="${BELA_PUBLIC_URL:-}"
SSH=(ssh -i "$KEY" -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=10)
SCP=(scp -q -i "$KEY" -o IdentitiesOnly=yes -o BatchMode=yes -o ConnectTimeout=10)
[ -f "$ROOT/dist/web/index.html" ] || { echo "dist/web nao existe: rode tools/build_web.sh"; exit 1; }
"${SSH[@]}" "$HOST" 'mkdir -p /root/bela/site.new && rm -rf /root/bela/site.new/*'
"${SCP[@]}" "$ROOT"/dist/web/* "$HOST:/root/bela/site.new/"
# troca quase atomica: o container serve /root/bela/site por bind mount (mesmo inode do diretorio)
"${SSH[@]}" "$HOST" 'cd /root/bela && find site -mindepth 1 -delete && cp -a site.new/. site/ && rm -rf site.new && ls site'
echo "Publicado ${URL:+em $URL}"
