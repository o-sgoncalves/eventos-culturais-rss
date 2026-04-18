# Goiânia Cultural

Agregador open source de eventos culturais de Goiânia/GO — música, teatro, cinema, arte e muito mais, coletados automaticamente do Instagram e curados por uma equipe local.

> **Licença:** GPL-3.0 | **Stack:** Python + FastAPI + React + PostgreSQL + Docker

---

## Instalação Rápida

### Pré-requisitos
- [Docker](https://docs.docker.com/get-docker/) e Docker Compose instalados
- Git

### 5 passos

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/eventos-culturais-rss.git
cd eventos-culturais-rss

# 2. Rode o setup interativo
chmod +x scripts/setup.sh
./scripts/setup.sh

# Pronto! O script cuida de tudo:
# - Cria o .env com segredos gerados automaticamente
# - Roda as migrations do banco
# - Cria o primeiro usuário admin
# - Sobe todos os serviços
```

Acesse:
- **Site:** http://localhost
- **Admin:** http://localhost/admin
- **API Docs:** http://localhost:8000/docs

---

## Adicionar contas do Instagram

**Via painel admin:** acesse http://localhost/admin → aba "Fontes Instagram" → adicionar `@nomeconta`

**Via código:** edite `rss-scraper/config.py`:

```python
instagram_accounts: List[str] = [
    "espacocultural_gyn",
    "casadoponte",
    "sua_nova_conta",  # adicione aqui
]
```

Reinicie o serviço: `docker compose restart rss-scraper`

---

## O que fazer quando o Instagram bloquear o scraper?

O sistema tem fallback automático (retorna cache antigo enquanto possível). Para importar posts manualmente:

```bash
# Prepare um arquivo posts.json com a estrutura:
# [{"url": "https://instagram.com/p/...", "caption": "texto do post", "date": "2026-04-25T20:00:00Z"}]

curl -X POST http://localhost:8001/import/nomeconta \
  -H "Content-Type: application/json" \
  -d @posts.json
```

---

## Estrutura do projeto

```
eventos-culturais-rss/
├── rss-scraper/    # Microserviço: Instagram → RSS
├── backend/        # API FastAPI + worker APScheduler
├── frontend/       # React + TypeScript + Tailwind
├── nginx/          # Reverse proxy config
└── scripts/        # setup.sh e utilitários
```

---

## Contribuindo

Leia [CONTRIBUTING.md](CONTRIBUTING.md) para guia completo.

TL;DR:
1. Fork → branch → commit → PR
2. Rode os testes: `pytest backend/tests/ -v` e `cd frontend && npm test`
3. PRs precisam passar no CI

---

## FAQ

**P: Funciona em produção (VPS)?**
Sim! Veja [docs/DEPLOY.md](docs/DEPLOY.md) para guia com SSL via Let's Encrypt.

**P: Posso usar para outras cidades?**
Sim — troque as contas do Instagram e o nome do projeto. O código não é específico de Goiânia.

**P: O Instagram pode banir meu IP?**
Sim, é um risco real. O sistema tem cache de 6h e fallback para importação manual. Use com moderação.
