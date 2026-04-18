# RSS Scraper Service — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** FastAPI microservice that converts Instagram accounts into RSS feeds, with 6h file-based cache and stale-on-error fallback.

**Architecture:** Instaloader fetches posts → feedgen builds RSS XML → file cache (`.xml` + `.meta`) persists results. If Instaloader fails and cache exists (even stale), returns cache with `X-Cache-Stale: true`. Manual import endpoint (`POST /import/{username}`) accepts JSON posts as fallback.

**Tech Stack:** Python 3.11, FastAPI 0.111, Instaloader 4.12, feedgen 1.0, slowapi 0.1.9, pydantic-settings 2.2, pytest + httpx

---

## File Map

| File | Responsibility |
|---|---|
| `rss-scraper/requirements.txt` | Dependencies |
| `rss-scraper/Dockerfile` | Container config |
| `rss-scraper/config.py` | Settings + account list |
| `rss-scraper/cache.py` | File cache read/write/validate |
| `rss-scraper/scrapers/__init__.py` | Package marker |
| `rss-scraper/scrapers/instagram_scraper.py` | Instaloader + feedgen + cache orchestration |
| `rss-scraper/main.py` | FastAPI routes |
| `rss-scraper/tests/__init__.py` | Package marker |
| `rss-scraper/tests/test_cache.py` | Cache unit tests |
| `rss-scraper/tests/test_scraper.py` | Scraper unit tests (Instaloader mocked) |
| `rss-scraper/tests/test_api.py` | API smoke tests |

---

## Task 1: Project Scaffold

**Files:**
- Create: `rss-scraper/requirements.txt`
- Create: `rss-scraper/Dockerfile`
- Create: `rss-scraper/config.py`
- Create: `rss-scraper/scrapers/__init__.py`
- Create: `rss-scraper/tests/__init__.py`
- Create: `rss-scraper/.env.example`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p rss-scraper/scrapers rss-scraper/tests rss-scraper/cache
touch rss-scraper/scrapers/__init__.py rss-scraper/tests/__init__.py
```

- [ ] **Step 2: Write `rss-scraper/requirements.txt`**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
instaloader==4.12
feedgen==1.0.0
slowapi==0.1.9
pydantic-settings==2.2.1
pytest==8.1.1
httpx==0.27.0
pytest-asyncio==0.23.6
```

- [ ] **Step 3: Write `rss-scraper/Dockerfile`**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/cache

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 4: Write `rss-scraper/config.py`**

```python
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    cache_ttl: int = 21600  # 6 horas em segundos
    cache_dir: str = "/app/cache"
    log_level: str = "INFO"

    instagram_accounts: List[str] = [
        "espacocultural_gyn",
        "casadoponte",
        "teatro_goiania",
        "centro_cultural_ufg",
        "sesc_goias",
    ]

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 5: Write `rss-scraper/.env.example`**

```
CACHE_TTL=21600
CACHE_DIR=/app/cache
LOG_LEVEL=INFO
```

- [ ] **Step 6: Commit**

```bash
git add rss-scraper/
git commit -m "feat(rss-scraper): project scaffold"
```

---

## Task 2: File Cache Module

**Files:**
- Create: `rss-scraper/cache.py`
- Create: `rss-scraper/tests/test_cache.py`

- [ ] **Step 1: Write failing tests in `rss-scraper/tests/test_cache.py`**

```python
import json
import time
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from cache import cache_paths, is_valid, write, read


@pytest.fixture
def tmp_cache(tmp_path):
    return str(tmp_path)


def test_cache_paths_creates_directory(tmp_path):
    subdir = str(tmp_path / "nested" / "cache")
    xml, meta = cache_paths("testuser", subdir)
    assert xml.parent.exists()
    assert xml.name == "testuser.xml"
    assert meta.name == "testuser.meta"


def test_is_valid_false_when_no_meta_file(tmp_cache):
    _, meta = cache_paths("ghost", tmp_cache)
    assert is_valid(meta, 3600) is False


def test_is_valid_true_within_ttl(tmp_cache):
    _, meta = cache_paths("fresh", tmp_cache)
    meta.write_text(json.dumps({"timestamp": time.time()}))
    assert is_valid(meta, 3600) is True


def test_is_valid_false_when_expired(tmp_cache):
    _, meta = cache_paths("old", tmp_cache)
    meta.write_text(json.dumps({"timestamp": time.time() - 7201}))
    assert is_valid(meta, 3600) is False


def test_is_valid_false_on_corrupt_meta(tmp_cache):
    _, meta = cache_paths("corrupt", tmp_cache)
    meta.write_text("not json")
    assert is_valid(meta, 3600) is False


def test_write_and_read_roundtrip(tmp_cache):
    xml, meta = cache_paths("user", tmp_cache)
    write(xml, meta, b"<rss>data</rss>")
    assert read(xml) == b"<rss>data</rss>"
    assert json.loads(meta.read_text())["timestamp"] > 0


def test_read_returns_none_when_missing(tmp_cache):
    xml, _ = cache_paths("missing", tmp_cache)
    assert read(xml) is None
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
cd rss-scraper
pip install -r requirements.txt
pytest tests/test_cache.py -v
```

Expected: `ModuleNotFoundError: No module named 'cache'`

- [ ] **Step 3: Write `rss-scraper/cache.py`**

```python
import json
import time
from pathlib import Path


def cache_paths(username: str, cache_dir: str) -> tuple[Path, Path]:
    base = Path(cache_dir)
    base.mkdir(parents=True, exist_ok=True)
    return base / f"{username}.xml", base / f"{username}.meta"


def is_valid(meta_path: Path, ttl: int) -> bool:
    if not meta_path.exists():
        return False
    try:
        meta = json.loads(meta_path.read_text())
        return time.time() - meta["timestamp"] < ttl
    except (json.JSONDecodeError, KeyError):
        return False


def write(xml_path: Path, meta_path: Path, rss_bytes: bytes) -> None:
    xml_path.write_bytes(rss_bytes)
    meta_path.write_text(json.dumps({"timestamp": time.time()}))


def read(xml_path: Path) -> bytes | None:
    if xml_path.exists():
        return xml_path.read_bytes()
    return None
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_cache.py -v
```

Expected: 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add rss-scraper/cache.py rss-scraper/tests/test_cache.py
git commit -m "feat(rss-scraper): file-based cache with TTL and stale support"
```

---

## Task 3: Instagram Scraper + RSS Builder

**Files:**
- Create: `rss-scraper/scrapers/instagram_scraper.py`
- Create: `rss-scraper/tests/test_scraper.py`

- [ ] **Step 1: Write failing tests in `rss-scraper/tests/test_scraper.py`**

```python
import json
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from scrapers.instagram_scraper import _build_rss, get_feed


def _fake_post(shortcode: str, caption: str, url: str = "") -> MagicMock:
    p = MagicMock()
    p.shortcode = shortcode
    p.caption = caption
    p.url = url
    p.date_utc = None
    return p


def test_build_rss_returns_valid_xml():
    posts = [_fake_post("abc123", "Show hoje às 20h! R$ 40")]
    result = _build_rss("testconta", posts)
    assert b"<rss" in result
    assert b"abc123" in result
    assert b"Show hoje" in result


def test_build_rss_empty_posts():
    result = _build_rss("testconta", [])
    assert b"<rss" in result


def test_build_rss_truncates_long_title():
    long_caption = "A" * 200
    posts = [_fake_post("abc", long_caption)]
    result = _build_rss("testconta", posts)
    # title should be truncated but RSS still valid
    assert b"<rss" in result


def test_get_feed_returns_hit_on_valid_cache(tmp_path, monkeypatch):
    monkeypatch.setattr("scrapers.instagram_scraper.settings.cache_dir", str(tmp_path))
    monkeypatch.setattr("scrapers.instagram_scraper.settings.cache_ttl", 3600)

    xml = tmp_path / "hituser.xml"
    meta = tmp_path / "hituser.meta"
    xml.write_bytes(b"<rss>cached</rss>")
    meta.write_text(json.dumps({"timestamp": time.time()}))

    rss, status = get_feed("hituser")
    assert status == "HIT"
    assert rss == b"<rss>cached</rss>"


def test_get_feed_returns_stale_when_instaloader_fails(tmp_path, monkeypatch):
    monkeypatch.setattr("scrapers.instagram_scraper.settings.cache_dir", str(tmp_path))
    monkeypatch.setattr("scrapers.instagram_scraper.settings.cache_ttl", 1)

    xml = tmp_path / "staleuser.xml"
    meta = tmp_path / "staleuser.meta"
    xml.write_bytes(b"<rss>stale</rss>")
    meta.write_text(json.dumps({"timestamp": 0}))  # expirado

    with patch("scrapers.instagram_scraper._fetch_fresh", side_effect=Exception("blocked")):
        rss, status = get_feed("staleuser")

    assert status == "STALE"
    assert rss == b"<rss>stale</rss>"


def test_get_feed_raises_when_no_cache_and_fetch_fails(tmp_path, monkeypatch):
    monkeypatch.setattr("scrapers.instagram_scraper.settings.cache_dir", str(tmp_path))
    monkeypatch.setattr("scrapers.instagram_scraper.settings.cache_ttl", 1)

    with patch("scrapers.instagram_scraper._fetch_fresh", side_effect=Exception("blocked")):
        with pytest.raises(Exception, match="blocked"):
            get_feed("nouser")


def test_get_feed_writes_cache_on_miss(tmp_path, monkeypatch):
    monkeypatch.setattr("scrapers.instagram_scraper.settings.cache_dir", str(tmp_path))
    monkeypatch.setattr("scrapers.instagram_scraper.settings.cache_ttl", 3600)

    fake_rss = b"<rss>fresh</rss>"
    with patch("scrapers.instagram_scraper._fetch_fresh", return_value=fake_rss):
        rss, status = get_feed("freshuser")

    assert status == "MISS"
    assert rss == fake_rss
    assert (tmp_path / "freshuser.xml").exists()
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_scraper.py -v
```

Expected: `ModuleNotFoundError: No module named 'scrapers.instagram_scraper'`

- [ ] **Step 3: Write `rss-scraper/scrapers/instagram_scraper.py`**

```python
import logging

import instaloader
from feedgen.feed import FeedGenerator

import cache as cache_mod
from config import settings

logger = logging.getLogger(__name__)

CacheStatus = str  # Literal["HIT", "MISS", "STALE"]


def _build_rss(username: str, posts: list) -> bytes:
    fg = FeedGenerator()
    fg.id(f"https://www.instagram.com/{username}/")
    fg.title(f"@{username} — Goiânia Cultural")
    fg.link(href=f"https://www.instagram.com/{username}/")
    fg.description(f"Posts recentes de @{username}")
    fg.language("pt-BR")

    for post in posts[:20]:
        fe = fg.add_entry()
        fe.id(f"https://www.instagram.com/p/{post.shortcode}/")
        caption = post.caption or ""
        fe.title(caption[:100] if caption else f"Post de @{username}")
        fe.link(href=f"https://www.instagram.com/p/{post.shortcode}/")
        fe.description(caption)
        if post.date_utc:
            fe.published(post.date_utc.isoformat() + "Z")
        if getattr(post, "url", None):
            fe.enclosure(post.url, 0, "image/jpeg")

    return fg.rss_str(pretty=True)


def _fetch_fresh(username: str) -> bytes:
    loader = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        compress_json=False,
        quiet=True,
    )
    profile = instaloader.Profile.from_username(loader.context, username)
    posts = list(profile.get_posts())
    return _build_rss(username, posts)


def get_feed(username: str) -> tuple[bytes, CacheStatus]:
    """Retorna (rss_bytes, status). Status: HIT | MISS | STALE."""
    xml_path, meta_path = cache_mod.cache_paths(username, settings.cache_dir)

    if cache_mod.is_valid(meta_path, settings.cache_ttl):
        return xml_path.read_bytes(), "HIT"

    try:
        rss = _fetch_fresh(username)
        cache_mod.write(xml_path, meta_path, rss)
        return rss, "MISS"
    except Exception as exc:
        logger.error("Instaloader falhou para @%s: %s", username, exc)
        stale = cache_mod.read(xml_path)
        if stale:
            return stale, "STALE"
        raise
```

- [ ] **Step 4: Run tests — verify they pass**

```bash
pytest tests/test_scraper.py -v
```

Expected: 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add rss-scraper/scrapers/instagram_scraper.py rss-scraper/tests/test_scraper.py
git commit -m "feat(rss-scraper): instagram scraper with stale-on-error cache"
```

---

## Task 4: FastAPI Application

**Files:**
- Create: `rss-scraper/main.py`
- Create: `rss-scraper/tests/test_api.py`

- [ ] **Step 1: Write failing tests in `rss-scraper/tests/test_api.py`**

```python
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_health():
    from main import app
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_accounts_returns_list():
    from main import app
    client = TestClient(app)
    response = client.get("/accounts")
    assert response.status_code == 200
    data = response.json()
    assert "accounts" in data
    assert isinstance(data["accounts"], list)


def test_feed_returns_rss_xml_on_success():
    from main import app
    client = TestClient(app)
    fake_rss = b"<?xml version='1.0'?><rss version='2.0'><channel><title>t</title></channel></rss>"
    with patch("main.get_feed", return_value=(fake_rss, "MISS")):
        response = client.get("/feed/testuser")
    assert response.status_code == 200
    assert "rss" in response.headers["content-type"]
    assert response.headers["x-cache"] == "MISS"
    assert response.headers["x-cache-stale"] == "false"


def test_feed_stale_header_when_cache_stale():
    from main import app
    client = TestClient(app)
    fake_rss = b"<rss/>"
    with patch("main.get_feed", return_value=(fake_rss, "STALE")):
        response = client.get("/feed/testuser")
    assert response.status_code == 200
    assert response.headers["x-cache-stale"] == "true"


def test_feed_returns_503_on_failure():
    from main import app
    client = TestClient(app)
    with patch("main.get_feed", side_effect=Exception("blocked")):
        response = client.get("/feed/baduser")
    assert response.status_code == 503


def test_import_posts_returns_202(tmp_path, monkeypatch):
    monkeypatch.setenv("CACHE_DIR", str(tmp_path))
    from main import app
    client = TestClient(app)
    posts = [
        {
            "url": "https://instagram.com/p/abc123/",
            "caption": "Show hoje às 20h! R$ 40",
            "date": "2026-04-18T20:00:00Z",
            "image_url": "https://example.com/img.jpg",
        }
    ]
    response = client.post("/import/testuser", json=posts)
    assert response.status_code == 202
    assert response.json()["imported"] == 1
    assert response.json()["username"] == "testuser"
```

- [ ] **Step 2: Run tests — verify they fail**

```bash
pytest tests/test_api.py -v
```

Expected: `ModuleNotFoundError: No module named 'main'`

- [ ] **Step 3: Write `rss-scraper/main.py`**

```python
import logging

from fastapi import FastAPI, HTTPException, Request, Response
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

import cache as cache_mod
from config import settings
from scrapers.instagram_scraper import get_feed

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Goiânia Cultural — RSS Scraper")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/health")
def health():
    return {"status": "ok", "service": "rss-scraper"}


@app.get("/accounts")
def list_accounts():
    return {"accounts": settings.instagram_accounts}


@app.get("/feed/{username}")
@limiter.limit("2/minute")
async def feed(username: str, request: Request):
    try:
        rss_bytes, cache_status = get_feed(username)
        headers = {
            "X-Cache": "HIT" if cache_status == "HIT" else "MISS",
            "X-Cache-Stale": "true" if cache_status == "STALE" else "false",
        }
        return Response(content=rss_bytes, media_type="application/rss+xml", headers=headers)
    except Exception as exc:
        logger.error("Erro no feed de @%s: %s", username, exc)
        raise HTTPException(
            status_code=503,
            detail=f"Feed indisponível para @{username}. Tente mais tarde.",
        )


@app.post("/import/{username}", status_code=202)
async def import_posts(username: str, posts: list[dict]):
    """Fallback manual: recebe lista de posts e gera RSS sem Instaloader."""
    from feedgen.feed import FeedGenerator

    fg = FeedGenerator()
    fg.id(f"https://www.instagram.com/{username}/")
    fg.title(f"@{username} — Goiânia Cultural (import manual)")
    fg.link(href=f"https://www.instagram.com/{username}/")
    fg.description(f"Posts importados manualmente de @{username}")
    fg.language("pt-BR")

    for post in posts:
        fe = fg.add_entry()
        fe.id(post.get("url", f"https://www.instagram.com/{username}/"))
        caption = post.get("caption", "")
        fe.title(caption[:100] if caption else f"Post de @{username}")
        fe.link(href=post.get("url", f"https://www.instagram.com/{username}/"))
        fe.description(caption)
        if post.get("date"):
            fe.published(post["date"])
        if post.get("image_url"):
            fe.enclosure(post["image_url"], 0, "image/jpeg")

    rss_bytes = fg.rss_str(pretty=True)
    xml_path, meta_path = cache_mod.cache_paths(username, settings.cache_dir)
    cache_mod.write(xml_path, meta_path, rss_bytes)

    return {"imported": len(posts), "username": username}
```

- [ ] **Step 4: Run all tests — verify they pass**

```bash
pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 5: Commit**

```bash
git add rss-scraper/main.py rss-scraper/tests/test_api.py
git commit -m "feat(rss-scraper): fastapi routes with rate limiting and manual import"
```

---

## Task 5: Docker Build Validation

**Files:**
- No new files — validates Dockerfile from Task 1

- [ ] **Step 1: Build the container**

```bash
cd rss-scraper
docker build -t goiania-rss-scraper:test .
```

Expected: build completes without error

- [ ] **Step 2: Run health check**

```bash
docker run --rm -d -p 8001:8000 --name rss-test goiania-rss-scraper:test
sleep 3
curl http://localhost:8001/health
docker stop rss-test
```

Expected: `{"status":"ok","service":"rss-scraper"}`

- [ ] **Step 3: Commit**

```bash
git add rss-scraper/
git commit -m "feat(rss-scraper): docker build validated"
```

---

## Phase 1 Complete

The RSS Scraper service is fully functional and tested. Verify with:

```bash
cd rss-scraper
pytest tests/ -v --tb=short
```

Expected: all tests green. Proceed to Phase 2 (Backend).
