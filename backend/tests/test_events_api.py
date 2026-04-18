from models import Event
from auth import hash_password
from models import User


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_list_events_empty(client):
    response = client.get("/api/events")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


def test_list_events_returns_only_approved(client, db):
    db.add(Event(title="Aprovado", approved=True, source_url="https://a.com"))
    db.add(Event(title="Pendente", approved=False, source_url="https://b.com"))
    db.commit()

    response = client.get("/api/events")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Aprovado"


def test_filter_by_category(client, db):
    db.add(Event(title="Show", approved=True, category="musica", source_url="https://c.com"))
    db.add(Event(title="Peça", approved=True, category="teatro", source_url="https://d.com"))
    db.commit()

    response = client.get("/api/events?category=musica")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["category"] == "musica"


def test_filter_free_only(client, db):
    db.add(Event(title="Free", approved=True, is_free=True, source_url="https://e.com"))
    db.add(Event(title="Paid", approved=True, is_free=False, price="R$ 50", source_url="https://f.com"))
    db.commit()

    response = client.get("/api/events?free=true")
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Free"


def test_suggest_event(client):
    payload = {"title": "Evento Sugerido", "description": "Teste", "category": "musica"}
    response = client.post("/api/events/suggest", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Evento Sugerido"
    assert data["approved"] is False
    assert data["submitted_by_user"] is True


def test_get_event_by_id(client, db):
    ev = Event(title="Detalhado", approved=True, source_url="https://g.com")
    db.add(ev)
    db.commit()
    db.refresh(ev)

    response = client.get(f"/api/events/{ev.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Detalhado"


def test_get_event_not_found(client):
    response = client.get("/api/events/99999")
    assert response.status_code == 404


def test_export_ics(client, db):
    import datetime
    ev = Event(title="Evento ICS", approved=True, source_url="https://ics.com",
               event_date=datetime.datetime(2026, 4, 25, 20, 0))
    db.add(ev)
    db.commit()
    db.refresh(ev)

    response = client.get(f"/api/events/{ev.id}/ics")
    assert response.status_code == 200
    assert "text/calendar" in response.headers["content-type"]
    assert b"BEGIN:VCALENDAR" in response.content
    assert b"Evento ICS" in response.content
