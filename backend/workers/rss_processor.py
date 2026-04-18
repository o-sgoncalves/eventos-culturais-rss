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

    source.last_scraped = datetime.utcnow()
    source.error_count = 0
    db.commit()
    return new_count


def run_once() -> None:
    db = SessionLocal()
    try:
        sources = db.query(Source).filter(Source.active == True).all()  # noqa: E712
        logger.info("Iniciando scraping de %d fontes", len(sources))
        total = sum(_process_source(s, db) for s in sources)
        logger.info("Scraping concluído. %d novos eventos salvos.", total)
    finally:
        db.close()


def main() -> None:
    logging.basicConfig(level=settings.log_level)
    logger.info("Worker iniciado. Agendado para 06h diariamente.")

    scheduler = BlockingScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(run_once, "cron", hour=6, minute=0)

    run_once()
    scheduler.start()


if __name__ == "__main__":
    main()
