# Backend API + Worker — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI backend with PostgreSQL persistence, JWT admin auth, REST API for events/sources, and APScheduler worker that consumes RSS feeds and extracts cultural events via regex.

**Architecture:** SQLAlchemy models → Alembic migrations → FastAPI routers (public + admin) → APScheduler worker runs daily at 06h, calls RSS Scraper service, extracts events via regex into the database as `approved=false`. Redis for rate limiting only (no Celery).

**Tech Stack:** Python 3.11, FastAPI 0.111, SQLAlchemy 2.0, Alembic, psycopg2, pydantic-settings, python-jose[cryptography], passlib[bcrypt], feedparser, APScheduler 3.10, slowapi, Redis (via redis-py), pytest + httpx

**Prerequisites:** Phase 1 (RSS Scraper) must be complete and running on port 8001.

---

## File Map

| File | Responsibility |
|---|---|
| `backend/requirements.txt` | Dependencies |
| `backend/Dockerfile` | Container config |
| `backend/config.py` | Settings from env vars |
| `backend/database.py` | SQLAlchemy engine + session factory |
| `backend/models.py` | ORM models: Event, Source, User |
| `backend/schemas.py` | Pydantic request/response schemas |
| `backend/auth.py` | Password hashing + JWT creation/validation |
| `backend/alembic.ini` | Alembic config |
| `backend/alembic/env.py` | Alembic migration env |
| `backend/alembic/versions/001_initial.py` | Initial schema migration |
| `backend/routers/__init__.py` | Package marker |
| `backend/routers/events.py` | Public event endpoints |
| `backend/routers/admin.py` | Admin endpoints (JWT-protected) |
| `backend/workers/__init__.py` | Package marker |
| `backend/workers/event_extractor.py` | Regex extraction: date, time, price, category |
| `backend/workers/rss_processor.py` | APScheduler + feedparser + orchestration |
| `backend/scripts/create_admin.py` | Interactive first-admin creation script |
| `backend/main.py` | FastAPI app, router registration |
| `backend/tests/__init__.py` | Package marker |
| `backend/tests/conftest.py` | Test DB setup, fixtures |
| `backend/tests/test_auth.py` | Auth unit tests |
| `backend/tests/test_extractor.py` | Regex extractor unit tests |
| `backend/tests/test_events_api.py` | Events API smoke tests |
| `backend/tests/test_admin_api.py` | Admin API smoke tests |

---

## Task 1: Project Scaffold

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`
- Create: `backend/config.py`
- Create: `backend/routers/__init__.py`
- Create: `backend/workers/__init__.py`
- Create: `backend/scripts/__init__.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/.env.example`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p backend/routers backend/workers backend/scripts backend/tests backend/alembic/versions
touch backend/routers/__init__.py backend/workers/__init__.py
touch backend/scripts/__init__.py backend/tests/__init__.py
```

- [ ] **Step 2: Write `backend/requirements.txt`**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
sqlalchemy==2.0.30
alembic==1.13.1
psycopg2-binary==2.9.9
pydantic-settings==2.2.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
feedparser==6.0.11
apscheduler==3.10.4
slowapi==0.1.9
redis==5.0.3
httpx==0.27.0
pytest==8.1.1
pytest-asyncio==0.23.6
```

- [ ] **Step 3: Write `backend/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 4: Write `backend/config.py`**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://goiania:secret@db:5432/goiania_cultural"
    redis_url: str = "redis://redis:6379"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    rss_service_url: str = "http://rss-scraper:8000"
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost", "http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 5: Write `backend/.env.example`**

```
DATABASE_URL=postgresql://goiania:your_password@db:5432/goiania_cultural
REDIS_URL=redis://redis:6379
JWT_SECRET=change-me-run-openssl-rand-hex-32
JWT_EXPIRE_HOURS=24
RSS_SERVICE_URL=http://rss-scraper:8000
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost","http://localhost:3000"]
```

- [ ] **Step 6: Commit**

```bash
git add backend/
git commit -m "feat(backend): project scaffold"
```

---

## Task 2: Database Models and Alembic

**Files:**
- Create: `backend/database.py`
- Create: `backend/models.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/versions/001_initial.py`

- [ ] **Step 1: Write `backend/database.py`**

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **Step 2: Write `backend/models.py`**

```python
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func

from database import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    event_date = Column(DateTime)
    event_time = Column(String(50))
    location = Column(String(255))
    address = Column(Text)
    region = Column(String(100))
    price = Column(String(100))
    is_free = Column(Boolean, default=False)
    category = Column(String(50))
    source_url = Column(Text, unique=True)
    image_url = Column(Text)
    approved = Column(Boolean, default=False)
    submitted_by_user = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True)
    platform = Column(String(50), default="instagram")
    username = Column(String(100), nullable=False, unique=True)
    active = Column(Boolean, default=True)
    last_scraped = Column(DateTime)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
```

- [ ] **Step 3: Write `backend/alembic.ini`**

```ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://goiania:secret@db:5432/goiania_cultural

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 4: Write `backend/alembic/env.py`**

```python
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config import settings
from database import Base
import models  # noqa: F401 — ensures models are registered

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 5: Write `backend/alembic/versions/001_initial.py`**

```python
"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-18
"""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(50), nullable=False, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("is_admin", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("platform", sa.String(50), server_default="instagram"),
        sa.Column("username", sa.String(100), nullable=False, unique=True),
        sa.Column("active", sa.Boolean(), server_default="true"),
        sa.Column("last_scraped", sa.DateTime()),
        sa.Column("error_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("event_date", sa.DateTime()),
        sa.Column("event_time", sa.String(50)),
        sa.Column("location", sa.String(255)),
        sa.Column("address", sa.Text()),
        sa.Column("region", sa.String(100)),
        sa.Column("price", sa.String(100)),
        sa.Column("is_free", sa.Boolean(), server_default="false"),
        sa.Column("category", sa.String(50)),
        sa.Column("source_url", sa.Text(), unique=True),
        sa.Column("image_url", sa.Text()),
        sa.Column("approved", sa.Boolean(), server_default="false"),
        sa.Column("submitted_by_user", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.text("now()")),
    )
    op.create_index("idx_events_date", "events", ["event_date"])
    op.create_index("idx_events_approved", "events", ["approved"])
    op.create_index("idx_events_category", "events", ["category"])
    op.create_index("idx_events_is_free", "events", ["is_free"])


def downgrade() -> None:
    op.drop_table("events")
    op.drop_table("sources")
    op.drop_table("users")
```

- [ ] **Step 6: Commit**

```bash
git add backend/database.py backend/models.py backend/alembic.ini backend/alembic/
git commit -m "feat(backend): sqlalchemy models and alembic migrations"
```

---

## Task 3: Auth Module

**Files:**
- Create: `backend/auth.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: Write failing tests in `backend/tests/test_auth.py`**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import hash_password, verify_password, create_token, decode_token


def test_hash_and_verify_password():
    hashed = hash_password("mysecret123")
    assert verify_password("mysecret123", hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_hash_is_not_plaintext():
    hashed = hash_password("mysecret123")
    assert hashed != "mysecret123"
    assert len(hashed) > 20


def test_create_and_decode_token():
    token = create_token({"sub": "admin", "user_id": 1})
    payload = decode_token(token)
    assert payload["sub"] == "admin"
    assert payload["user_id"] == 1


def test_decode_invalid_token_returns_none():
    result = decode_token("not.a.valid.token")
    assert result is None


def test_decode_tampered_token_returns_none():
    token = create_token({"sub": "admin"})
    tampered = token[:-5] + "XXXXX"
    assert decode_token(tampered) is None
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd backend
pip install -r requirements.txt
pytest tests/test_auth.py -v
```

Expected: `ModuleNotFoundError: No module named 'auth'`

- [ ] **Step 3: Write `backend/auth.py`**

```python
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import settings

_pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    return _pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_ctx.verify(plain, hashed)


def create_token(data: dict[str, Any]) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=settings.jwt_expire_hours)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except JWTError:
        return None
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_auth.py -v
```

Expected: 5 tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/auth.py backend/tests/test_auth.py
git commit -m "feat(backend): jwt auth and bcrypt password hashing"
```

---

## Task 4: Pydantic Schemas

**Files:**
- Create: `backend/schemas.py`

No tests — schemas are validated by the API tests in later tasks.

- [ ] **Step 1: Write `backend/schemas.py`**

```python
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# --- Events ---

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    event_time: Optional[str] = None
    location: Optional[str] = None
    address: Optional[str] = None
    region: Optional[str] = None
    price: Optional[str] = None
    is_free: bool = False
    category: Optional[str] = None
    source_url: Optional[str] = None
    image_url: Optional[str] = None


class EventCreate(EventBase):
    title: str


class EventUpdate(EventBase):
    pass


class EventOut(EventBase):
    id: int
    approved: bool
    submitted_by_user: bool
    created_at: datetime

    class Config:
        from_attributes = True


class EventSuggest(BaseModel):
    title: str
    description: Optional[str] = None
    event_date: Optional[datetime] = None
    location: Optional[str] = None
    price: Optional[str] = None
    category: Optional[str] = None


# --- Sources ---

class SourceCreate(BaseModel):
    username: str
    platform: str = "instagram"


class SourceOut(BaseModel):
    id: int
    platform: str
    username: str
    active: bool
    last_scraped: Optional[datetime]
    error_count: int
    created_at: datetime

    class Config:
        from_attributes = True


# --- Auth ---

class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# --- Stats ---

class StatsOut(BaseModel):
    total_events: int
    pending_events: int
    approved_events: int
    by_category: dict[str, int]
```

- [ ] **Step 2: Commit**

```bash
git add backend/schemas.py
git commit -m "feat(backend): pydantic schemas"
```

---

## Task 5: Event Extractor (Regex)

**Files:**
- Create: `backend/workers/event_extractor.py`
- Create: `backend/tests/test_extractor.py`

- [ ] **Step 1: Write failing tests in `backend/tests/test_extractor.py`**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from workers.event_extractor import extract_date, extract_time, extract_price, detect_category, is_free_event, extract_event_data


def test_extract_date_slash_format():
    result = extract_date("Show dia 25/04/2026 no Casarão")
    assert result is not None
    assert result.day == 25
    assert result.month == 4


def test_extract_date_keyword_dia():
    result = extract_date("Evento dia 10 de abril")
    assert result is not None
    assert result.day == 10


def test_extract_date_returns_none_when_absent():
    assert extract_date("Sem data nenhuma aqui") is None


def test_extract_time_with_h():
    assert extract_time("Começa às 20h no Espaço") == "20:00"


def test_extract_time_with_h_minutes():
    assert extract_time("Abertura 19h30") == "19:30"


def test_extract_time_colon_format():
    assert extract_time("A partir das 21:00") == "21:00"


def test_extract_time_returns_none_when_absent():
    assert extract_time("Sem horário definido") is None


def test_extract_price_real():
    assert extract_price("Ingresso R$ 40") == "R$ 40"


def test_extract_price_range():
    result = extract_price("Ingressos de R$ 30 a R$ 80")
    assert "30" in result and "80" in result


def test_extract_price_returns_none_when_absent():
    assert extract_price("Sem info de preço") is None


def test_is_free_gratuis():
    assert is_free_event("Entrada franca para todos") is True
    assert is_free_event("Acesso gratuito") is True
    assert is_free_event("Show grátis!") is True
    assert is_free_event("Free admission") is True


def test_is_free_false_when_paid():
    assert is_free_event("Ingresso R$ 50") is False


def test_detect_category_music():
    assert detect_category("Grande show com banda ao vivo") == "musica"


def test_detect_category_theater():
    assert detect_category("Peça de teatro imperdível") == "teatro"


def test_detect_category_exposition():
    assert detect_category("Exposição de arte contemporânea") == "exposicao"


def test_detect_category_returns_outros():
    assert detect_category("Algo sem categoria definida") == "outros"


def test_extract_event_data_full_text():
    text = """
    Show da Banda Xpto no Casarão Cultural
    Dia 25/04 às 20h
    Ingresso: R$ 40
    Setor Bueno, Goiânia
    """
    result = extract_event_data(text, source_url="https://instagram.com/p/test")
    assert result["title"] is not None
    assert result["event_time"] == "20:00"
    assert result["price"] == "R$ 40"
    assert result["category"] == "musica"
    assert result["is_free"] is False
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_extractor.py -v
```

Expected: `ModuleNotFoundError: No module named 'workers.event_extractor'`

- [ ] **Step 3: Write `backend/workers/event_extractor.py`**

```python
import re
from datetime import datetime
from typing import Optional

CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "musica":     ["show", "banda", "música", "concerto", "forró", "samba", "jazz", "rock", "pagode"],
    "teatro":     ["peça", "teatro", "espetáculo", "dramaturgia", "ator", "atriz"],
    "cinema":     ["filme", "cinema", "sessão", "curta", "documentário", "projeção"],
    "festa":      ["festa", "balada", "party", "dj", "open bar", "aniversário"],
    "exposicao":  ["exposição", "mostra", "instalação", "vernissage", "galeria"],
    "arte":       ["arte visual", "arte urbana", "grafite", "intervenção"],
    "workshop":   ["workshop", "oficina", "curso", "aula", "capacitação"],
    "palestra":   ["palestra", "debate", "mesa redonda", "seminário", "simpósio"],
    "esporte":    ["corrida", "torneio", "campeonato", "esporte", "maratona"],
    "gastronomia": ["gastronômico", "culinária", "chef", "degustação", "foodfest"],
}

FREE_PATTERNS = re.compile(
    r"\b(grátis|gratuito|entrada\s+franca|free|acesso\s+gratuito)\b", re.IGNORECASE
)

DATE_PATTERNS = [
    re.compile(r"\b(\d{1,2})[/\-](\d{1,2})(?:[/\-](\d{2,4}))?\b"),
    re.compile(r"\bdia\s+(\d{1,2})\b", re.IGNORECASE),
]

MONTH_NAMES = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8,
    "setembro": 9, "outubro": 10, "novembro": 11, "dezembro": 12,
}

TIME_PATTERNS = [
    re.compile(r"\b(\d{1,2})h(\d{2})\b", re.IGNORECASE),  # 20h30
    re.compile(r"\b(\d{1,2})h\b", re.IGNORECASE),          # 20h
    re.compile(r"\b(\d{1,2}):(\d{2})\b"),                   # 20:00
]

PRICE_PATTERNS = [
    re.compile(r"R\$\s*(\d+)\s*(?:a|ao?)\s*R\$\s*(\d+)"),  # range
    re.compile(r"R\$\s*(\d+(?:[,.]\d{2})?)"),               # single
]


def extract_date(text: str) -> Optional[datetime]:
    now = datetime.now()

    # Try DD/MM or DD/MM/YYYY
    m = DATE_PATTERNS[0].search(text)
    if m:
        try:
            day, month = int(m.group(1)), int(m.group(2))
            year = int(m.group(3)) if m.group(3) else now.year
            if year < 100:
                year += 2000
            return datetime(year, month, day)
        except ValueError:
            pass

    # Try "dia NN de MMMM"
    m = re.search(r"\bdia\s+(\d{1,2})(?:\s+de\s+(\w+))?", text, re.IGNORECASE)
    if m:
        try:
            day = int(m.group(1))
            month_name = (m.group(2) or "").lower()
            month = MONTH_NAMES.get(month_name, now.month)
            return datetime(now.year, month, day)
        except ValueError:
            pass

    return None


def extract_time(text: str) -> Optional[str]:
    # 20h30
    m = TIME_PATTERNS[0].search(text)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"

    # 20h
    m = TIME_PATTERNS[1].search(text)
    if m:
        return f"{int(m.group(1)):02d}:00"

    # 20:00
    m = TIME_PATTERNS[2].search(text)
    if m:
        return f"{int(m.group(1)):02d}:{m.group(2)}"

    return None


def extract_price(text: str) -> Optional[str]:
    # Range: R$ 30 a R$ 80
    m = PRICE_PATTERNS[0].search(text)
    if m:
        return f"R$ {m.group(1)} a R$ {m.group(2)}"

    # Single: R$ 40
    m = PRICE_PATTERNS[1].search(text)
    if m:
        return f"R$ {m.group(1)}"

    return None


def is_free_event(text: str) -> bool:
    return bool(FREE_PATTERNS.search(text))


def detect_category(text: str) -> str:
    text_lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return category
    return "outros"


def extract_event_data(text: str, source_url: str, image_url: str = None) -> dict:
    """Extrai dados de evento a partir do texto de um post do Instagram."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    title = lines[0][:255] if lines else "Evento sem título"

    price = extract_price(text)
    free = is_free_event(text)
    if free:
        price = price or "Gratuito"

    return {
        "title": title,
        "description": text,
        "event_date": extract_date(text),
        "event_time": extract_time(text),
        "price": price,
        "is_free": free,
        "category": detect_category(text),
        "source_url": source_url,
        "image_url": image_url,
        "approved": False,
    }
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_extractor.py -v
```

Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/workers/event_extractor.py backend/tests/test_extractor.py
git commit -m "feat(backend): regex event extractor (date, time, price, category)"
```

---

## Task 6: Public Events Router

**Files:**
- Create: `backend/routers/events.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_events_api.py`

- [ ] **Step 1: Write `backend/tests/conftest.py`**

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

TEST_DB_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
```

- [ ] **Step 2: Write failing tests in `backend/tests/test_events_api.py`**

```python
from models import Event
from auth import hash_password
from models import User


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_list_events_empty(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_events_returns_only_approved(client, db):
    db.add(Event(title="Aprovado", approved=True, source_url="https://a.com"))
    db.add(Event(title="Pendente", approved=False, source_url="https://b.com"))
    db.commit()

    response = client.get("/api/events")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Aprovado"


def test_filter_by_category(client, db):
    db.add(Event(title="Show", approved=True, category="musica", source_url="https://c.com"))
    db.add(Event(title="Peça", approved=True, category="teatro", source_url="https://d.com"))
    db.commit()

    response = client.get("/api/events?category=musica")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["category"] == "musica"


def test_filter_free_only(client, db):
    db.add(Event(title="Free", approved=True, is_free=True, source_url="https://e.com"))
    db.add(Event(title="Paid", approved=True, is_free=False, price="R$ 50", source_url="https://f.com"))
    db.commit()

    response = client.get("/api/events?free=true")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Free"


def test_suggest_event(client):
    payload = {"title": "Evento Sugerido", "description": "Teste", "category": "musica"}
    response = client.post("/api/events/suggest", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Evento Sugerido"
    assert data["approved"] is False
    assert data["submitted_by_user"] is True


def test_get_event_by_id(client, db):
    ev = Event(title="Detalhado", approved=True, source_url="https://g.com")
    db.add(ev)
    db.commit()
    db.refresh(ev)

    response = client.get(f"/api/events/{ev.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Detalhado"


def test_get_event_not_found(client):
    response = client.get("/api/events/99999")
    assert response.status_code == 404
```

- [ ] **Step 3: Write `backend/routers/events.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Event
from schemas import EventOut, EventSuggest

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=dict)
def list_events(
    db: Session = Depends(get_db),
    category: str | None = None,
    free: bool | None = None,
    region: str | None = None,
    q: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = db.query(Event).filter(Event.approved == True)  # noqa: E712

    if category:
        query = query.filter(Event.category == category)
    if free is True:
        query = query.filter(Event.is_free == True)  # noqa: E712
    if region:
        query = query.filter(Event.region.ilike(f"%{region}%"))
    if q:
        query = query.filter(Event.title.ilike(f"%{q}%") | Event.description.ilike(f"%{q}%"))

    total = query.count()
    items = query.order_by(Event.event_date.asc().nullslast()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [EventOut.model_validate(e) for e in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id, Event.approved == True).first()  # noqa: E712
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event


@router.post("/suggest", response_model=EventOut, status_code=201)
def suggest_event(payload: EventSuggest, db: Session = Depends(get_db)):
    event = Event(**payload.model_dump(), submitted_by_user=True, approved=False)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
```

- [ ] **Step 4: Create minimal `backend/main.py`** (will be extended in Task 8)

```python
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import events

logging.basicConfig(level=settings.log_level)

app = FastAPI(title="Goiânia Cultural API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "goiania-cultural-api"}
```

- [ ] **Step 5: Run tests — verify they pass**

```bash
pytest tests/test_events_api.py -v
```

Expected: all tests PASS

- [ ] **Step 6: Commit**

```bash
git add backend/routers/events.py backend/tests/conftest.py backend/tests/test_events_api.py backend/main.py
git commit -m "feat(backend): public events API with filtering and suggestions"
```

---

## Task 6b: ICS Export Endpoint

**Files:**
- Modify: `backend/routers/events.py` (add route)

- [ ] **Step 1: Add ICS generation to `backend/routers/events.py`** (append to existing file)

```python
# Adicionar ao final de backend/routers/events.py
from fastapi.responses import Response as FastAPIResponse
from datetime import timezone


@router.get("/{event_id}/ics")
def export_ics(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id, Event.approved == True).first()  # noqa: E712
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    # Monta arquivo iCal (RFC 5545) sem dependências externas
    dt_stamp = __import__("datetime").datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    if event.event_date:
        dtstart = event.event_date.strftime("%Y%m%dT%H%M%SZ")
        dtend = event.event_date.strftime("%Y%m%dT%H%M%SZ")
    else:
        dtstart = dt_stamp
        dtend = dt_stamp

    ics = "\r\n".join([
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Goiânia Cultural//PT",
        "BEGIN:VEVENT",
        f"UID:{event.id}@goiania-cultural",
        f"DTSTAMP:{dt_stamp}",
        f"DTSTART:{dtstart}",
        f"DTEND:{dtend}",
        f"SUMMARY:{event.title}",
        f"DESCRIPTION:{(event.description or '').replace(chr(10), '\\n')[:500]}",
        f"LOCATION:{event.location or ''}",
        "END:VEVENT",
        "END:VCALENDAR",
        "",
    ])

    return FastAPIResponse(
        content=ics.encode("utf-8"),
        media_type="text/calendar; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="evento-{event_id}.ics"'},
    )
```

- [ ] **Step 2: Add test to `backend/tests/test_events_api.py`**

```python
def test_export_ics(client, db):
    ev = Event(title="Evento ICS", approved=True, source_url="https://ics.com",
               event_date=__import__("datetime").datetime(2026, 4, 25, 20, 0))
    db.add(ev)
    db.commit()
    db.refresh(ev)

    response = client.get(f"/api/events/{ev.id}/ics")
    assert response.status_code == 200
    assert "text/calendar" in response.headers["content-type"]
    assert b"BEGIN:VCALENDAR" in response.content
    assert b"Evento ICS" in response.content
```

- [ ] **Step 3: Run tests**

```bash
pytest tests/test_events_api.py -v
```

Expected: all tests PASS including new ICS test

- [ ] **Step 4: Commit**

```bash
git add backend/routers/events.py backend/tests/test_events_api.py
git commit -m "feat(backend): ics export endpoint for calendar integration"
```

---

## Task 7: Admin Router (JWT-protected)

**Files:**
- Create: `backend/routers/admin.py`
- Create: `backend/tests/test_admin_api.py`

- [ ] **Step 1: Write failing tests in `backend/tests/test_admin_api.py`**

```python
from models import Event, Source, User
from auth import hash_password


def _create_admin(db):
    user = User(username="admin", email="admin@test.com", password_hash=hash_password("secret123"))
    db.add(user)
    db.commit()
    return user


def _get_token(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "secret123"})
    return response.json()["access_token"]


def test_login_success(client, db):
    _create_admin(db)
    response = client.post("/api/auth/login", json={"username": "admin", "password": "secret123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, db):
    _create_admin(db)
    response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_pending_events_requires_auth(client):
    response = client.get("/api/admin/events/pending")
    assert response.status_code == 401


def test_pending_events_returns_list(client, db):
    _create_admin(db)
    token = _get_token(client)
    db.add(Event(title="Pendente", approved=False, source_url="https://p.com"))
    db.commit()

    response = client.get("/api/admin/events/pending", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Pendente"


def test_approve_event(client, db):
    _create_admin(db)
    token = _get_token(client)
    ev = Event(title="Aprovável", approved=False, source_url="https://ap.com")
    db.add(ev)
    db.commit()
    db.refresh(ev)

    response = client.put(
        f"/api/admin/events/{ev.id}/approve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    db.refresh(ev)
    assert ev.approved is True


def test_reject_event(client, db):
    _create_admin(db)
    token = _get_token(client)
    ev = Event(title="Rejeitável", approved=False, source_url="https://rj.com")
    db.add(ev)
    db.commit()
    db.refresh(ev)

    response = client.delete(
        f"/api/admin/events/{ev.id}/reject",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert db.query(Event).filter(Event.id == ev.id).first() is None


def test_add_source(client, db):
    _create_admin(db)
    token = _get_token(client)

    response = client.post(
        "/api/admin/sources",
        json={"username": "novaconta", "platform": "instagram"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["username"] == "novaconta"


def test_stats(client, db):
    _create_admin(db)
    token = _get_token(client)
    db.add(Event(title="E1", approved=True, category="musica", source_url="https://s1.com"))
    db.add(Event(title="E2", approved=False, source_url="https://s2.com"))
    db.commit()

    response = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_events"] == 2
    assert data["pending_events"] == 1
    assert data["by_category"]["musica"] == 1
```

- [ ] **Step 2: Write `backend/routers/admin.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import create_token, decode_token, verify_password
from database import get_db
from models import Event, Source, User
from schemas import EventOut, EventUpdate, LoginRequest, SourceCreate, SourceOut, StatsOut, TokenResponse

router = APIRouter(tags=["admin"])
_bearer = HTTPBearer()


def _require_admin(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return user


@router.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = create_token({"sub": user.username, "user_id": user.id})
    return TokenResponse(access_token=token)


@router.get("/api/admin/events/pending", response_model=list[EventOut])
def pending_events(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    return db.query(Event).filter(Event.approved == False).order_by(Event.created_at.desc()).all()  # noqa: E712


@router.put("/api/admin/events/{event_id}/approve", response_model=EventOut)
def approve_event(event_id: int, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    event.approved = True
    db.commit()
    db.refresh(event)
    return event


@router.delete("/api/admin/events/{event_id}/reject")
def reject_event(event_id: int, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    db.delete(event)
    db.commit()
    return {"detail": "Evento removido"}


@router.put("/api/admin/events/{event_id}", response_model=EventOut)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


@router.post("/api/admin/events", response_model=EventOut, status_code=201)
def create_event(payload: EventUpdate, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    event = Event(**payload.model_dump(), approved=True)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/api/admin/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    return db.query(Source).all()


@router.post("/api/admin/sources", response_model=SourceOut, status_code=201)
def add_source(payload: SourceCreate, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    existing = db.query(Source).filter(Source.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Conta já cadastrada")
    source = Source(**payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.delete("/api/admin/sources/{source_id}")
def remove_source(source_id: int, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Fonte não encontrada")
    db.delete(source)
    db.commit()
    return {"detail": "Fonte removida"}


@router.post("/api/admin/trigger-scrape", status_code=202)
def trigger_scrape(_: User = Depends(_require_admin)):
    from workers.rss_processor import run_once
    import threading
    threading.Thread(target=run_once, daemon=True).start()
    return {"detail": "Scraping iniciado em background"}


@router.get("/api/admin/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    total = db.query(Event).count()
    pending = db.query(Event).filter(Event.approved == False).count()  # noqa: E712
    approved = db.query(Event).filter(Event.approved == True).count()  # noqa: E712
    by_cat = dict(
        db.query(Event.category, func.count(Event.id))
        .filter(Event.category != None)  # noqa: E711
        .group_by(Event.category)
        .all()
    )
    return StatsOut(total_events=total, pending_events=pending, approved_events=approved, by_category=by_cat)
```

- [ ] **Step 3: Update `backend/main.py`** to include the admin router

```python
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from routers import events, admin

logging.basicConfig(level=settings.log_level)

app = FastAPI(title="Goiânia Cultural API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(events.router)
app.include_router(admin.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "goiania-cultural-api"}
```

- [ ] **Step 4: Run all tests — verify they pass**

```bash
pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add backend/routers/admin.py backend/tests/test_admin_api.py backend/main.py
git commit -m "feat(backend): admin API with JWT auth, event approval, source management"
```

---

## Task 8: RSS Processor Worker

**Files:**
- Create: `backend/workers/rss_processor.py`

No separate tests — the extractor is already tested; processor integration tested via trigger-scrape endpoint.

- [ ] **Step 1: Write `backend/workers/rss_processor.py`**

```python
import logging
from datetime import datetime

import feedparser
import httpx
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy.exc import IntegrityError

from config import settings
from database import SessionLocal
from models import Event, Source
from workers.event_extractor import extract_event_data

logger = logging.getLogger(__name__)


def _process_source(source: Source, db) -> int:
    """Busca RSS de uma fonte e salva eventos novos. Retorna count de novos eventos."""
    url = f"{settings.rss_service_url}/feed/{source.username}"
    try:
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
    except Exception as exc:
        logger.error("Falha ao buscar feed de @%s: %s", source.username, exc)
        source.error_count += 1
        db.commit()
        return 0

    feed = feedparser.parse(response.content)
    new_count = 0

    for entry in feed.entries:
        text = entry.get("description") or entry.get("summary") or entry.get("title", "")
        source_url = entry.get("link", "")
        image_url = None
        if hasattr(entry, "enclosures") and entry.enclosures:
            image_url = entry.enclosures[0].get("url")

        if not text or not source_url:
            continue

        # Skip if already in DB
        if db.query(Event).filter(Event.source_url == source_url).first():
            continue

        data = extract_event_data(text, source_url=source_url, image_url=image_url)
        event = Event(**data)
        db.add(event)
        try:
            db.commit()
            new_count += 1
            logger.info("Novo evento salvo: %s", data["title"][:60])
        except IntegrityError:
            db.rollback()

    source.last_scraped = datetime.utcnow()
    source.error_count = 0
    db.commit()
    return new_count


def run_once() -> None:
    """Processa todas as fontes ativas uma vez."""
    db = SessionLocal()
    try:
        sources = db.query(Source).filter(Source.active == True).all()  # noqa: E712
        logger.info("Iniciando scraping de %d fontes", len(sources))
        total = sum(_process_source(s, db) for s in sources)
        logger.info("Scraping concluído. %d novos eventos salvos.", total)
    finally:
        db.close()


def main() -> None:
    """Ponto de entrada do worker com scheduler diário."""
    logging.basicConfig(level=settings.log_level)
    logger.info("Worker iniciado. Agendado para 06h diariamente.")

    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(run_once, "cron", hour=6, minute=0)

    # Executa uma vez na inicialização para não esperar o próximo dia
    run_once()
    scheduler.start()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add backend/workers/rss_processor.py
git commit -m "feat(backend): apscheduler rss processor worker (runs daily at 06h)"
```

---

## Task 9: Create Admin Script

**Files:**
- Create: `backend/scripts/create_admin.py`

- [ ] **Step 1: Write `backend/scripts/create_admin.py`**

```python
"""Script interativo para criar o primeiro usuário administrador."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from auth import hash_password
from database import SessionLocal, engine
from models import Base, User


def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    print("\n=== Criar Usuário Admin — Goiânia Cultural ===\n")
    username = input("Username: ").strip()
    email = input("Email: ").strip()
    password = input("Senha (mínimo 8 caracteres): ").strip()

    if len(password) < 8:
        print("Erro: senha muito curta.")
        sys.exit(1)

    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"Erro: usuário '{username}' já existe.")
        sys.exit(1)

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        is_admin=True,
    )
    db.add(user)
    db.commit()

    print(f"\n✅ Admin '{username}' criado com sucesso!")
    print("   Acesse /admin para fazer login.\n")
    db.close()


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add backend/scripts/create_admin.py
git commit -m "feat(backend): interactive create_admin script"
```

---

## Task 10: Full Test Suite Run

- [ ] **Step 1: Run all backend tests**

```bash
cd backend
pytest tests/ -v --tb=short
```

Expected: all tests PASS. If SQLite doesn't support some PostgreSQL-specific constructs, the conftest.py already handles this via SQLite override.

- [ ] **Step 2: Validate Docker build**

```bash
docker build -t goiania-backend:test ./backend
```

Expected: build succeeds

- [ ] **Step 3: Final commit**

```bash
git add backend/
git commit -m "feat(backend): phase 2 complete — API + worker + auth"
```

---

## Phase 2 Complete

Backend API is fully functional. Proceed to Phase 3 (Frontend + Infrastructure).
