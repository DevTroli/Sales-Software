#!/bin/bash
set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}🚀 BUILD DO SALES SOFTWARE NO VERCEL${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Detectar Python disponível
PYTHON_CMD=""
for py_version in python3.12 python3.11 python3.10 python3; do
    if command -v $py_version &> /dev/null; then
        PYTHON_CMD=$py_version
        break
    fi
done

if [ -z "$PYTHON_CMD" ]; then
    echo -e "${RED}❌ ERRO CRÍTICO: Nenhuma versão do Python foi encontrada!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python encontrado: $PYTHON_CMD${NC}"
echo -e "${GREEN}✅ Versão: $($PYTHON_CMD --version)${NC}"
echo ""

# PASSO 1: Validar variáveis de ambiente
echo -e "${BLUE}1️⃣  VALIDANDO VARIÁVEIS DE AMBIENTE${NC}"
if [ -z "$SECRET_KEY" ]; then
    echo -e "${RED}❌ ERRO: SECRET_KEY não foi definida no Vercel!${NC}"
    exit 1
fi
echo -e "${GREEN}   ✓ SECRET_KEY definida (${#SECRET_KEY} caracteres)${NC}"

if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ ERRO: DATABASE_URL não foi definida no Vercel!${NC}"
    exit 1
fi
echo -e "${GREEN}   ✓ DATABASE_URL definida (${#DATABASE_URL} caracteres)${NC}"

if [ -z "$DJANGO_SETTINGS_MODULE" ]; then
    echo -e "${YELLOW}⚠️  DJANGO_SETTINGS_MODULE não definida, usando setup.staging${NC}"
    export DJANGO_SETTINGS_MODULE=setup.staging
fi
echo -e "${GREEN}   ✓ DJANGO_SETTINGS_MODULE = $DJANGO_SETTINGS_MODULE${NC}"
echo ""

# PASSO 2: Instalar dependências
echo -e "${BLUE}2️⃣  INSTALANDO DEPENDÊNCIAS DO PYTHON${NC}"
$PYTHON_CMD -m pip install --upgrade pip setuptools wheel --quiet
echo -e "${GREEN}   ✓ pip, setuptools, wheel atualizados${NC}"

$PYTHON_CMD -m pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERRO: Falha ao instalar requirements.txt${NC}"
    exit 1
fi
echo -e "${GREEN}   ✓ Todas as dependências instaladas${NC}"
echo ""

# PASSO 3: Executar migrations
echo -e "${BLUE}3️⃣  EXECUTANDO MIGRATIONS DO BANCO DE DADOS${NC}"
echo -e "${YELLOW}   Conectando ao NeonDB...${NC}"

# Primeiro, verifica se consegue conectar ao banco
$PYTHON_CMD manage.py dbshell --no-color <<EOF
\q
EOF

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERRO: Não conseguiu conectar ao banco de dados!${NC}"
    echo -e "${YELLOW}   Verifique se DATABASE_URL está correta:${NC}"
    echo -e "${YELLOW}   DATABASE_URL começa com 'postgresql://'?${NC}"
    exit 1
fi

echo -e "${GREEN}   ✓ Conexão com banco bem-sucedida${NC}"

# Executa as migrations
echo -e "${YELLOW}   Aplicando migrations...${NC}"
$PYTHON_CMD manage.py migrate --noinput --verbosity=2

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ ERRO: As migrations falharam!${NC}"
    echo -e "${YELLOW}   Tentando diagnosticar...${NC}"
    $PYTHON_CMD manage.py showmigrations
    exit 1
fi

echo -e "${GREEN}   ✓ Migrations aplicadas com sucesso${NC}"
echo ""

# PASSO 4: Limpar sessões expiradas (importante em serverless!)
echo -e "${BLUE}4️⃣ LIMPANDO SESSÕES EXPIRADAS${NC}"
$PYTHON_CMD manage.py cleanup_sessions --verbosity=0 2>/dev/null || true
echo -e "${GREEN} ✓ Sessões expiradas limpas${NC}"
echo ""

# PASSO 5: Coletar arquivos estáticos
echo -e "${BLUE}4️⃣  COLETANDO ARQUIVOS ESTÁTICOS${NC}"
$PYTHON_CMD manage.py collectstatic --noinput --clear --verbosity=1 > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}   ⚠️  Coleta de estáticos falhou, mas continuando...${NC}"
else
    echo -e "${GREEN}   ✓ Arquivos estáticos coletados${NC}"
fi
echo ""

# Build concluído com sucesso
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ BUILD CONCLUÍDO COM SUCESSO!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${GREEN}📊 RESUMO:${NC}"
echo -e "   ✓ Python $($PYTHON_CMD --version | awk '{print $2}') detectado"
echo -e "   ✓ Variáveis de ambiente validadas"
echo -e "   ✓ Dependências Python instaladas"
echo -e "   ✓ Banco de dados conectado"
echo -e "   ✓ Migrations aplicadas"
echo -e "   ✓ Arquivos estáticos coletados"
echo ""
echo -e "${YELLOW}🚀 Seu app está pronto para servir requisições!${NC}"
echo ""
