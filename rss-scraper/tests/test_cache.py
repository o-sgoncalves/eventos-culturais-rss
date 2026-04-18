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
