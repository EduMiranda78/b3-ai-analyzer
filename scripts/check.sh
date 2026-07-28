#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(
    cd "$(dirname "${BASH_SOURCE[0]}")/.."
    pwd
)"

cd "$ROOT_DIR"

if [[ ! -d ".venv" ]]; then
    echo "ERRO: ambiente .venv não encontrado."
    exit 1
fi

source .venv/bin/activate

echo "1. Verificando sintaxe Python"

python -m compileall -q \
    main.py \
    wsgi.py \
    services \
    tests

echo "2. Executando testes"

python -m pytest

echo "3. Verificando JavaScript"

if command -v node >/dev/null 2>&1; then
    node --check static/js/main.js
else
    echo "Node.js não instalado. Etapa ignorada."
fi

echo "4. Verificando templates"

if grep -RIn \
    '^[[:space:]]*```[[:space:]]*$' \
    templates
then
    echo "ERRO: crases encontradas nos templates."
    exit 1
fi

echo "5. Verificando diferenças Git"

git diff --check

echo
echo "Todas as verificações foram concluídas."
