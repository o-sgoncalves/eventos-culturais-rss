import logging
from datetime import datetime, timezone

import feedparser
import httpx
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlalchemy.exc import IntegrityError

from config import settings
from database import SessionLocal
from models import Event, Source
from workers.event_extractor import extract_event_data

logger = logging.getLogger(__name__)


def _process_source(source: Source, db) -> int:  # db is a fresh session per call from run_once
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

    source.last_scraped = datetime.now(timezone.utc)
    source.error_count = 0
    db.commit()
    return new_count


def run_once() -> None:
    with SessionLocal() as list_db:
        sources = list_db.query(Source).filter(Source.active == True).all()  # noqa: E712
    logger.info("Iniciando scraping de %d fontes", len(sources))
    total = 0
    for source in sources:
        with SessionLocal() as db:
            total += _process_source(source, db)
    logger.info("Scraping concluído. %d novos eventos salvos.", total)


def main() -> None:
    logging.basicConfig(level=settings.log_level)
    logger.info("Worker iniciado. Agendado para 06h diariamente.")

    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(run_once, "cron", hour=6, minute=0)

    run_once()
    scheduler.start()


if __name__ == "__main__":
    main()
