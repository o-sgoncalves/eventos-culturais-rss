# Design: Goiânia Cultural

**Data:** 2026-04-18  
**Status:** Aprovado  
**Repositório:** eventos-culturais-rss  

---

## Resumo

Sistema web open source (GPL-3.0) que agrega eventos culturais de Goiânia/GO a partir de contas do Instagram, permitindo que o público encontre eventos de forma centralizada. Administradores aprovam eventos antes de publicar. A comunidade pode sugerir eventos via formulário.

---

## Decisões de Design

| Decisão | Escolha | Motivo |
|---|---|---|
| Scraping strategy | Instaloader + fallback manual (JSON/CSV) | Resiliência quando Instagram bloquear |
| Visual style | Dark mode nativo (roxo #6c63ff + teal #3ecfb2) | Combina com clima noturno de eventos |
| Deployment | Local (docker-compose.yml) + Produção (docker-compose.prod.yml + docs) | Fácil setup local sem complicar para quem quer subir em VPS |
| Implementação | Sequencial por serviço: rss-scraper → backend → frontend | Core primeiro, cada serviço testado isoladamente |
| Worker scheduling | APScheduler (sem Celery) | Simples para MVP; Redis fica só para cache/rate-limit do backend |
| Cache do scraper | Arquivo local (não Redis) | Isolamento total do serviço de scraping |
| Migrations | Alembic | Evolução segura do schema em produção |
| Nome do projeto | Goiânia Cultural | Repositório mantém `eventos-culturais-rss` |

---

## Arquitetura

```
Instagram (@contas) 
    ↓ Instaloader
[RSS Scraper Service] :8001
    - GET /feed/{username}   → RSS XML
    - GET /health
    - GET /accounts
    - POST /import/{username} → fallback manual JSON/CSV
    - Cache em arquivo (TTL 6h, stale-on-error)
    - Rate limit: 1 req/conta a cada 30s (slowapi)
    ↓ RSS XML
[Worker] APScheduler 06h diária
    - Consome RSS de todas as fontes ativas
    - Extrai eventos via regex (data, hora, preço, local, categoria)
    - Salva como approved=false
    ↓
[Backend API] :8000  FastAPI + PostgreSQL + Redis
    ↓ JSON
[Frontend] React + TypeScript + Tailwind dark mode
    ↓ HTTP :80
[Nginx] reverse proxy (local) / + SSL Let's Encrypt (prod)
    ↓
Usuário público / Admin
```

---

## Estrutura de Diretórios

```
goiania-cultural/
├── README.md                        # PT-BR, instalação em ≤5 passos
├── README.en.md
├── CONTRIBUTING.md
├── LICENSE                          # GPL-3.0
├── docker-compose.yml               # Local: todos os 7 serviços
├── docker-compose.prod.yml          # Produção: nginx com SSL
├── .env.example
├── scripts/
│   └── setup.sh                     # Interativo: cria .env, gera JWT_SECRET, migrations, cria admin
├── docs/
│   ├── INSTALL.md
│   ├── ARCHITECTURE.md
│   ├── API.md
│   ├── DEPLOY.md                    # Guia VPS + SSL
│   └── superpowers/specs/           # Specs de design
├── .github/
│   └── workflows/
│       ├── ci.yml                   # Lint + testes em PRs
│       └── build.yml                # Build dos containers
├── rss-scraper/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                      # FastAPI app
│   ├── config.py                    # INSTAGRAM_ACCOUNTS list
│   ├── scrapers/
│   │   └── instagram_scraper.py     # Instaloader wrapper + cache
│   └── tests/
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py
│   ├── models.py                    # SQLAlchemy ORM
│   ├── schemas.py                   # Pydantic schemas
│   ├── database.py
│   ├── auth.py                      # JWT (python-jose + passlib/bcrypt)
│   ├── config.py
│   ├── alembic/                     # Migrations
│   ├── workers/
│   │   └── rss_processor.py         # APScheduler, consome RSS, extrai eventos
│   ├── scripts/
│   │   └── create_admin.py
│   └── tests/
├── frontend/
│   ├── Dockerfile
│   ├── package.json                 # React 18, TypeScript, Tailwind, Vite
│   ├── src/
│   │   ├── App.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx             # Lista de eventos + filtros
│   │   │   ├── Admin.tsx            # Painel admin (login + dashboard)
│   │   │   └── SubmitEvent.tsx      # Formulário público
│   │   ├── components/
│   │   │   ├── EventCard.tsx        # Card dark mode
│   │   │   ├── Filters.tsx          # Chips mobile + sidebar desktop
│   │   │   └── Calendar.tsx         # Visualização calendário
│   │   └── api/
│   │       └── client.ts            # Axios/fetch wrapper
│   └── public/
└── nginx/
    ├── nginx.conf                   # Local
    └── nginx.prod.conf              # Produção + SSL
```

---

## Banco de Dados

```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    event_date TIMESTAMP,
    event_time VARCHAR(50),
    location VARCHAR(255),
    address TEXT,
    region VARCHAR(100),
    price VARCHAR(100),
    is_free BOOLEAN DEFAULT FALSE,
    category VARCHAR(50),
    source_url TEXT UNIQUE,
    image_url TEXT,
    approved BOOLEAN DEFAULT FALSE,
    submitted_by_user BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE sources (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50) DEFAULT 'instagram',
    username VARCHAR(100) NOT NULL UNIQUE,
    active BOOLEAN DEFAULT TRUE,
    last_scraped TIMESTAMP,
    error_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_admin BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_events_date ON events(event_date);
CREATE INDEX idx_events_approved ON events(approved);
CREATE INDEX idx_events_category ON events(category);
CREATE INDEX idx_events_is_free ON events(is_free);
```

---

## API Endpoints

### Público

| Método | Rota | Descrição |
|---|---|---|
| GET | `/api/events` | Lista eventos aprovados. Query: `date`, `category`, `free`, `region`, `q`, `page` |
| GET | `/api/events/{id}` | Detalhe do evento |
| GET | `/api/events/{id}/ics` | Exporta evento como .ics |
| POST | `/api/events/suggest` | Submissão pública (vai para aprovação) |
| GET | `/health` | Health check |

### Admin (JWT obrigatório)

| Método | Rota | Descrição |
|---|---|---|
| POST | `/api/auth/login` | Login, retorna JWT |
| GET | `/api/admin/events/pending` | Eventos aguardando aprovação |
| PUT | `/api/admin/events/{id}/approve` | Aprovar evento |
| PUT | `/api/admin/events/{id}/reject` | Rejeitar evento |
| PUT | `/api/admin/events/{id}` | Editar evento |
| POST | `/api/admin/events` | Cadastrar evento manualmente |
| GET | `/api/admin/sources` | Listar fontes Instagram |
| POST | `/api/admin/sources` | Adicionar conta Instagram |
| DELETE | `/api/admin/sources/{id}` | Remover conta |
| POST | `/api/admin/trigger-scrape` | Forçar scraping agora |
| POST | `/api/import` | Import manual JSON/CSV (fallback) |
| GET | `/api/admin/stats` | Estatísticas do dashboard |

---

## RSS Scraper: Comportamento de Cache

- Cache válido (< 6h): retorna XML, header `X-Cache: HIT`
- Cache expirado mas Instaloader ok: atualiza cache, retorna XML, header `X-Cache: MISS`
- Cache expirado e Instaloader falha: retorna cache antigo, header `X-Cache-Stale: true` + log de erro
- Sem cache e Instaloader falha: retorna HTTP 503 com mensagem clara

---

## Extração de Eventos (Regex Patterns)

```python
# Data
r'\b(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?\b'          # 25/04, 25-04-2025
r'\bdia\s+(\d{1,2})\b'                                         # dia 25
r'\b(segunda|terça|quarta|quinta|sexta|sábado|domingo)\b'      # dia da semana

# Hora
r'\b(\d{1,2})h(?:(\d{2}))?\b'                                 # 20h, 20h30
r'\b(\d{1,2}):(\d{2})\b'                                      # 20:00

# Preço
r'R\$\s*(\d+(?:[,.]\d{2})?)'                                  # R$ 50, R$ 30,00
r'\b(grátis|gratuito|entrada\s+franca|free)\b'                 # gratuito
r'R\$\s*(\d+)\s*(?:a|ao?)\s*R\$\s*(\d+)'                     # R$ 30 a R$ 80

# Categoria (keywords → categoria)
CATEGORY_KEYWORDS = {
    "musica":     ["show", "banda", "música", "concerto", "forró", "samba", "jazz"],
    "teatro":     ["peça", "teatro", "espetáculo", "dramaturgia"],
    "cinema":     ["filme", "cinema", "sessão", "curta", "documentário"],
    "festa":      ["festa", "balada", "party", "dj", "open bar"],
    "arte":       ["galeria", "vernissage", "arte visual", "arte urbana"],
    "exposicao":  ["exposição", "mostra", "instalação"],
    "workshop":   ["workshop", "oficina", "curso", "aula"],
    "palestra":   ["palestra", "debate", "mesa redonda", "seminário"],
}
```

---

## Frontend: Componentes Principais

### Home.tsx
- Header com logo "Goiânia Cultural" (roxo/branco) + botão "Sugerir Evento"
- Barra de busca
- Filtros: chips horizontais em mobile, sidebar em desktop (≥768px)
- Grid de `EventCard` com paginação (carregar mais)
- Filtros disponíveis: data (hoje/semana/mês/personalizado), categoria, região, apenas gratuitos, busca texto

### EventCard.tsx
- Imagem com gradiente por categoria (fallback quando sem imagem do Instagram)
- Badge de categoria (canto superior esquerdo)
- Badge "GRATUITO" ou preço (canto superior direito)
- Título, data, hora, local
- Ícones: compartilhar (Web Share API) + adicionar ao calendário (.ics)

### Admin.tsx
- Login com JWT armazenado em `localStorage`
- Dashboard: contador de pendentes (destacado), eventos recentes, stats por categoria
- Lista de pendentes com approve/reject inline
- Formulário de edição de evento
- Gerenciamento de fontes Instagram

---

## Infraestrutura Docker

### Serviços (docker-compose.yml)
1. `rss-scraper` — FastAPI, porta 8001, volume `rss_cache`
2. `api` — FastAPI, porta 8000, depende de `db` + `redis` + `rss-scraper`
3. `worker` — mesmo container do backend, comando `python workers/rss_processor.py`
4. `db` — PostgreSQL 15-alpine, volume `postgres_data`
5. `redis` — Redis 7-alpine, volume `redis_data`
6. `frontend` — Dockerfile faz `npm run build` e serve os arquivos estáticos com nginx (não dev server), porta 3000
7. `nginx` — reverse proxy, porta 80

### scripts/setup.sh
```bash
#!/bin/bash
# 1. Copia .env.example → .env
# 2. Gera JWT_SECRET com openssl rand -hex 32
# 3. Pergunta senha do admin (DB_PASSWORD)
# 4. docker-compose up -d db redis
# 5. docker-compose run --rm api alembic upgrade head
# 6. docker-compose run --rm api python scripts/create_admin.py
# 7. docker-compose up -d
# 8. echo "✅ Setup completo! Acesse http://localhost"
```

---

## GitHub Actions

### ci.yml (em PRs)
- Python: `ruff check` + `pytest` (backend e rss-scraper)
- Node: `eslint` + `vitest` (frontend)

### build.yml (em PRs e main)
- `docker build` de cada serviço para validar Dockerfiles

---

## Testes Mínimos (smoke tests)

### Backend
- `GET /health` retorna 200
- `POST /api/auth/login` com credenciais válidas retorna JWT
- `GET /api/events` retorna lista (pode estar vazia)
- Parser regex extrai data/preço corretamente de strings de exemplo

### Frontend
- Página principal renderiza sem erros
- Filtros atualizam a lista de eventos

### RSS Scraper
- `GET /health` retorna 200
- Cache é escrito e lido corretamente
- Resposta stale quando Instaloader falha (mock)

---

## Segurança

- Senhas: bcrypt via `passlib`
- JWT: `python-jose`, expiração configurável (padrão 24h)
- CORS: apenas origens configuradas via `.env`
- Rate limiting: `slowapi` no backend + no scraper
- `.env` nunca commitado (`.gitignore`)
- Inputs validados via Pydantic (backend) e Zod (frontend)

---

## Contas Instagram Iniciais (exemplos)

```python
INSTAGRAM_ACCOUNTS = [
    "espacocultural_gyn",
    "casadoponte",
    "teatro_goiania",
    "centro_cultural_ufg",
    "sesc_goias",
]
```

Usuário adiciona mais via painel admin ou editando `rss-scraper/config.py`.

---

## Fora de Escopo (MVP)

- Notificações por email/push
- Integração com Google Maps
- Comentários/avaliações de eventos
- Multi-cidade (só Goiânia)
- Scraping de outras redes sociais
- App mobile nativo
