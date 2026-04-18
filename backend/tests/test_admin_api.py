from models import Event, Source, User
from auth import hash_password


def _create_admin(db):
    user = User(username="admin", email="admin@test.com", password_hash=hash_password("secret123"))
    db.add(user)
    db.commit()
    return user


def _get_token(client):
    response = client.post("/api/auth/login", json={"username": "admin", "password": "secret123"})
    return response.json()["access_token"]


def test_login_success(client, db):
    _create_admin(db)
    response = client.post("/api/auth/login", json={"username": "admin", "password": "secret123"})
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password(client, db):
    _create_admin(db)
    response = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401


def test_pending_events_requires_auth(client):
    response = client.get("/api/admin/events/pending")
    assert response.status_code == 401


def test_pending_events_returns_list(client, db):
    _create_admin(db)
    token = _get_token(client)
    db.add(Event(title="Pendente", approved=False, source_url="https://p.com"))
    db.commit()

    response = client.get("/api/admin/events/pending", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Pendente"


def test_approve_event(client, db):
    _create_admin(db)
    token = _get_token(client)
    ev = Event(title="Aprovável", approved=False, source_url="https://ap.com")
    db.add(ev)
    db.commit()
    db.refresh(ev)

    response = client.put(
        f"/api/admin/events/{ev.id}/approve",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    db.refresh(ev)
    assert ev.approved is True


def test_reject_event(client, db):
    _create_admin(db)
    token = _get_token(client)
    ev = Event(title="Rejeitável", approved=False, source_url="https://rj.com")
    db.add(ev)
    db.commit()
    db.refresh(ev)

    response = client.delete(
        f"/api/admin/events/{ev.id}/reject",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert db.query(Event).filter(Event.id == ev.id).first() is None


def test_add_source(client, db):
    _create_admin(db)
    token = _get_token(client)

    response = client.post(
        "/api/admin/sources",
        json={"username": "novaconta", "platform": "instagram"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    assert response.json()["username"] == "novaconta"


def test_stats(client, db):
    _create_admin(db)
    token = _get_token(client)
    db.add(Event(title="E1", approved=True, category="musica", source_url="https://s1.com"))
    db.add(Event(title="E2", approved=False, source_url="https://s2.com"))
    db.commit()

    response = client.get("/api/admin/stats", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_events"] == 2
    assert data["pending_events"] == 1
    assert data["by_category"]["musica"] == 1
