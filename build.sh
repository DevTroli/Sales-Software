#!/bin/bash

set -e

echo "========================================"
echo "🔨 INICIANDO BUILD DO DJANGO"
echo "========================================"

echo ""
echo "1️⃣  Instalando dependências..."
python3.11 -m pip install -r requirements.txt --quiet

echo ""
echo "2️⃣  Executando migrations do banco de dados..."
echo "   (Criando todas as tabelas necessárias)"
python3.11 manage.py migrate --noinput --verbosity=2

echo ""
echo "3️⃣  Coletando arquivos estáticos..."
python3.11 manage.py collectstatic --noinput --clear --verbosity=2

echo ""
echo "✅ BUILD FINALIZADO COM SUCESSO!"
echo "========================================"
