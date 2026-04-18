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
