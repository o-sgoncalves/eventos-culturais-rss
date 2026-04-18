import logging

from fastapi import FastAPI, HTTPException, Path, Request, Response
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
async def feed(
    request: Request,
    username: str = Path(pattern=r"^[a-zA-Z0-9._]{1,30}$"),
):
    try:
        rss_bytes, cache_status = get_feed(username)
        headers = {
            "X-Cache": cache_status,
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
async def import_posts(
    posts: list[dict],
    username: str = Path(pattern=r"^[a-zA-Z0-9._]{1,30}$"),
):
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
