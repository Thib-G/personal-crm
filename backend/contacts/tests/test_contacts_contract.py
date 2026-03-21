"""
T027/T028 - Contract tests for POST /api/contacts/ and GET /api/contacts/{id}/
TDD: These tests drive the implementation. Run them — they MUST fail first.
"""
import uuid
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User

from crm.api import api

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="testuser", password="pass")


@pytest.mark.django_db
def test_create_contact_success(user):
    contact_id = str(uuid.uuid4())
    response = client.post(
        "/contacts/",
        json={
            "id": contact_id,
            "name": "Alice Dupont",
            "context_tag": "work",
            "organisation": "Acme Corp",
            "created_at": "2026-03-20T10:00:00Z",
            "created_lat": 50.8503,
            "created_lng": 4.3517,
            "phones": [{"id": str(uuid.uuid4()), "number": "+32491000000"}],
            "emails": [{"id": str(uuid.uuid4()), "address": "alice@acme.com"}],
        },
        user=user,
    )
    assert response.status_code == 201, response.content
    data = response.json()
    assert data["id"] == contact_id
    assert data["name"] == "Alice Dupont"
    assert data["context_tag"] == "work"
    assert len(data["phones"]) == 1
    assert len(data["emails"]) == 1


@pytest.mark.django_db
def test_create_contact_minimal(user):
    contact_id = str(uuid.uuid4())
    response = client.post(
        "/contacts/",
        json={
            "id": contact_id,
            "name": "Bob",
            "context_tag": "personal",
            "created_at": "2026-03-20T10:00:00Z",
        },
        user=user,
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Bob"


@pytest.mark.django_db
def test_create_contact_blank_name(user):
    response = client.post(
        "/contacts/",
        json={"id": str(uuid.uuid4()), "name": "", "context_tag": "work", "created_at": "2026-03-20T10:00:00Z"},
        user=user,
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_create_contact_invalid_context_tag(user):
    response = client.post(
        "/contacts/",
        json={"id": str(uuid.uuid4()), "name": "X", "context_tag": "invalid", "created_at": "2026-03-20T10:00:00Z"},
        user=user,
    )
    assert response.status_code == 422


@pytest.mark.django_db
def test_create_contact_duplicate_id(user):
    contact_id = str(uuid.uuid4())
    payload = {"id": contact_id, "name": "Carol", "context_tag": "event", "created_at": "2026-03-20T10:00:00Z"}
    client.post("/contacts/", json=payload, user=user)
    response = client.post("/contacts/", json=payload, user=user)
    assert response.status_code == 409


@pytest.mark.django_db
def test_create_contact_requires_auth():
    response = client.post(
        "/contacts/",
        json={"id": str(uuid.uuid4()), "name": "X", "context_tag": "work", "created_at": "2026-03-20T10:00:00Z"},
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_get_contact_success(user):
    contact_id = str(uuid.uuid4())
    client.post(
        "/contacts/",
        json={"id": contact_id, "name": "Dave", "context_tag": "work", "created_at": "2026-03-20T10:00:00Z"},
        user=user,
    )
    response = client.get(f"/contacts/{contact_id}/", user=user)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == contact_id
    assert data["name"] == "Dave"
    assert "phones" in data
    assert "emails" in data
    assert "history" in data
    assert "interaction_entries" in data


@pytest.mark.django_db
def test_get_contact_not_found(user):
    response = client.get(f"/contacts/{uuid.uuid4()}/", user=user)
    assert response.status_code == 404


@pytest.mark.django_db
def test_get_contact_requires_auth():
    response = client.get(f"/contacts/{uuid.uuid4()}/")
    assert response.status_code == 401
