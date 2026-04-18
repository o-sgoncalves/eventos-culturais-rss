import itertools
import logging
from typing import Literal

import instaloader
from feedgen.feed import FeedGenerator

import cache as cache_mod
from config import settings

logger = logging.getLogger(__name__)

CacheStatus = Literal["HIT", "MISS", "STALE"]


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
    posts = list(itertools.islice(profile.get_posts(), 20))
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
