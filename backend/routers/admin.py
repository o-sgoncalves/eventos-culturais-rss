from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func
from sqlalchemy.orm import Session

from auth import create_token, decode_token, verify_password
from database import get_db
from models import Event, Source, User
from schemas import EventOut, EventUpdate, LoginRequest, SourceCreate, SourceOut, StatsOut, TokenResponse

router = APIRouter(tags=["admin"])
_bearer = HTTPBearer(auto_error=False)


def _require_admin(
    credentials: HTTPAuthorizationCredentials = Security(_bearer),
    db: Session = Depends(get_db),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Acesso negado")
    return user


@router.post("/api/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    token = create_token({"sub": user.username, "user_id": user.id})
    return TokenResponse(access_token=token)


@router.get("/api/admin/events/pending", response_model=list[EventOut])
def pending_events(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    return db.query(Event).filter(Event.approved == False).order_by(Event.created_at.desc()).all()  # noqa: E712


@router.put("/api/admin/events/{event_id}/approve", response_model=EventOut)
def approve_event(event_id: int, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    event.approved = True
    db.commit()
    db.refresh(event)
    return event


@router.delete("/api/admin/events/{event_id}/reject")
def reject_event(event_id: int, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    db.delete(event)
    db.commit()
    return {"detail": "Evento removido"}


@router.put("/api/admin/events/{event_id}", response_model=EventOut)
def update_event(event_id: int, payload: EventUpdate, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


@router.post("/api/admin/events", response_model=EventOut, status_code=201)
def create_event(payload: EventUpdate, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    event = Event(**payload.model_dump(), approved=True)
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.get("/api/admin/sources", response_model=list[SourceOut])
def list_sources(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    return db.query(Source).all()


@router.post("/api/admin/sources", response_model=SourceOut, status_code=201)
def add_source(payload: SourceCreate, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    existing = db.query(Source).filter(Source.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Conta já cadastrada")
    source = Source(**payload.model_dump())
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


@router.delete("/api/admin/sources/{source_id}")
def remove_source(source_id: int, db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Fonte não encontrada")
    db.delete(source)
    db.commit()
    return {"detail": "Fonte removida"}


@router.post("/api/admin/trigger-scrape", status_code=202)
def trigger_scrape(_: User = Depends(_require_admin)):
    import logging as _logging
    import threading
    from workers.rss_processor import run_once
    _logging.getLogger(__name__).info("Scraping manual disparado via admin")
    threading.Thread(target=run_once, daemon=True).start()
    return {"detail": "Scraping iniciado em background"}


@router.get("/api/admin/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    total = db.query(Event).count()
    pending = db.query(Event).filter(Event.approved == False).count()  # noqa: E712
    approved = db.query(Event).filter(Event.approved == True).count()  # noqa: E712
    by_cat = dict(
        db.query(Event.category, func.count(Event.id))
        .filter(Event.category != None)  # noqa: E711
        .group_by(Event.category)
        .all()
    )
    return StatsOut(total_events=total, pending_events=pending, approved_events=approved, by_category=by_cat)


@router.post("/api/import", status_code=201)
def import_events(events: list[dict], db: Session = Depends(get_db), _: User = Depends(_require_admin)):
    existing_urls = {
        url for (url,) in db.query(Event.source_url).filter(
            Event.source_url.in_([item.get("source_url") for item in events if item.get("source_url")])
        ).all()
    }
    new_events = []
    for item in events:
        if item.get("source_url") in existing_urls:
            continue
        new_events.append(Event(
            title=item.get("title", "Evento importado"),
            description=item.get("description"),
            event_date=item.get("event_date"),
            location=item.get("location"),
            price=item.get("price"),
            is_free=item.get("is_free", False),
            category=item.get("category"),
            source_url=item.get("source_url"),
            image_url=item.get("image_url"),
            approved=False,
        ))
    if new_events:
        db.add_all(new_events)
        db.commit()
    return {"imported": len(new_events)}
