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
