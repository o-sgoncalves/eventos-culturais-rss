from datetime import datetime, time, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response as FastAPIResponse
from sqlalchemy.orm import Session

from slowapi import Limiter
from slowapi.util import get_remote_address

from database import get_db
from models import Event
from schemas import EventOut, EventSuggest

router = APIRouter(prefix="/api/events", tags=["events"])
limiter = Limiter(key_func=get_remote_address)


@router.get("", response_model=dict)
def list_events(
    db: Session = Depends(get_db),
    category: str | None = None,
    free: bool | None = None,
    region: str | None = None,
    q: str | None = None,
    date: str | None = None,
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

    if date:
        from datetime import date as DateType, timedelta
        today = DateType.today()
        if date == "hoje":
            query = query.filter(
                Event.event_date >= datetime.combine(today, time.min),
                Event.event_date < datetime.combine(today + timedelta(days=1), time.min),
            )
        elif date == "semana":
            week_end = today + timedelta(days=7)
            query = query.filter(
                Event.event_date >= datetime.combine(today, time.min),
                Event.event_date < datetime.combine(week_end, time.min),
            )
        elif date == "mes":
            month_end = today + timedelta(days=30)
            query = query.filter(
                Event.event_date >= datetime.combine(today, time.min),
                Event.event_date < datetime.combine(month_end, time.min),
            )
        else:
            try:
                target = DateType.fromisoformat(date)
                query = query.filter(
                    Event.event_date >= datetime.combine(target, time.min),
                    Event.event_date < datetime.combine(target + timedelta(days=1), time.min),
                )
            except ValueError:
                pass

    total = query.count()
    items = query.order_by(Event.event_date.asc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "items": [EventOut.model_validate(e) for e in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/{event_id}/ics")
def export_ics(event_id: int, db: Session = Depends(get_db)):
    import datetime as dt
    event = db.query(Event).filter(Event.id == event_id, Event.approved == True).first()  # noqa: E712
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")

    dt_stamp = dt.datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
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
        f"DESCRIPTION:{(event.description or '').replace(chr(10), chr(92) + 'n')[:500]}",
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


@router.get("/{event_id}", response_model=EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(Event).filter(Event.id == event_id, Event.approved == True).first()  # noqa: E712
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    return event


@router.post("/suggest", response_model=EventOut, status_code=201)
@limiter.limit("10/minute")
async def suggest_event(request: Request, payload: EventSuggest, db: Session = Depends(get_db)):
    event = Event(**payload.model_dump(), submitted_by_user=True, approved=False)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
