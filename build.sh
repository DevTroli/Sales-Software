#!/bin/bash
set -e

echo "=========================================="
echo "BUILD DO VERCEL - SALES SOFTWARE"
echo "=========================================="

PYTHON_CMD=python3.11
if ! command -v $PYTHON_CMD &> /dev/null; then
    PYTHON_CMD=python3
fi

echo ""
echo "✅ Usando: $PYTHON_CMD"

echo ""
echo "1️⃣  INSTALANDO DEPENDÊNCIAS..."
$PYTHON_CMD -m pip install --upgrade pip setuptools wheel > /dev/null 2>&1
$PYTHON_CMD -m pip install -r requirements.txt

echo ""
echo "2️⃣  VERIFICANDO CONFIGURAÇÕES..."
echo "   DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE:-'NÃO DEFINIDO'}"
echo "   DATABASE_URL definida: $([ -n "$DATABASE_URL" ] && echo 'SIM' || echo 'NÃO')"

if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERRO: SECRET_KEY não foi definida!"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERRO: DATABASE_URL não foi definida!"
    exit 1
fi

echo ""
echo "3️⃣  EXECUTANDO MIGRATIONS..."
$PYTHON_CMD manage.py migrate --noinput --verbosity=2

echo ""
echo "4️⃣  COLETANDO ARQUIVOS ESTÁTICOS..."
$PYTHON_CMD manage.py collectstatic --noinput --clear --verbosity=1

echo ""
echo "✅ BUILD CONCLUÍDO COM SUCESSO!"
