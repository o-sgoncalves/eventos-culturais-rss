from pathlib import Path
from unittest.mock import patch, MagicMock

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


def test_import_posts_returns_202(tmp_path):
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
    with patch("main.cache_mod.cache_paths") as mock_paths, \
         patch("main.cache_mod.write"):
        xml_path = tmp_path / "testuser.xml"
        meta_path = tmp_path / "testuser.meta"
        mock_paths.return_value = (xml_path, meta_path)
        response = client.post("/import/testuser", json=posts)
    assert response.status_code == 202
    assert response.json()["imported"] == 1
    assert response.json()["username"] == "testuser"
