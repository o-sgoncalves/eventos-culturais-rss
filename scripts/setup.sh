#!/usr/bin/env bash
set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║       Goiânia Cultural — Setup           ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# 1. Criar .env a partir do exemplo
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✓ Arquivo .env criado"
else
  echo "  .env já existe, mantendo"
fi

# 2. Gerar JWT_SECRET aleatório
JWT_SECRET=$(openssl rand -hex 32)
sed -i "s/JWT_SECRET=troque_por_chave_secreta/JWT_SECRET=${JWT_SECRET}/" .env
echo "✓ JWT_SECRET gerado"

# 3. Pedir senha do banco
echo ""
read -rsp "🔑 Defina uma senha para o banco de dados: " DB_PASSWORD
echo ""
sed -i "s/DB_PASSWORD=troque_por_senha_forte/DB_PASSWORD=${DB_PASSWORD}/" .env
echo "✓ Senha do banco configurada"

# 4. Subir dependências (db + redis)
echo ""
echo "⏳ Iniciando banco de dados e Redis..."
docker compose up -d db redis
echo "   Aguardando banco ficar pronto..."
sleep 8

# 5. Rodar migrations
echo "⏳ Rodando migrations..."
docker compose run --rm api alembic upgrade head
echo "✓ Migrations aplicadas"

# 6. Criar admin
echo ""
echo "👤 Criando usuário administrador..."
docker compose run --rm api python scripts/create_admin.py

# 7. Subir tudo
echo ""
echo "⏳ Subindo todos os serviços..."
docker compose up -d

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  ✅ Setup completo! Sistema no ar.       ║"
echo "║                                          ║"
echo "║  🌐 Site:      http://localhost          ║"
echo "║  🔐 Admin:     http://localhost/admin    ║"
echo "║  📖 API Docs:  http://localhost:8000/docs║"
echo "╚══════════════════════════════════════════╝"
echo ""
