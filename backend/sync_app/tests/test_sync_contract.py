"""T086/T087 - Sync pull/push contract tests."""
import uuid
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from django.utils import timezone
from crm.api import api
from contacts.tests.factories import ContactFactory, InteractionEntryFactory

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="syncuser", password="pass")


@pytest.mark.django_db
def test_sync_pull_returns_200(user):
    response = client.get("/sync/pull/?since=2020-01-01T00:00:00Z", user=user)
    assert response.status_code == 200
    data = response.json()
    assert "contacts" in data
    assert "tombstones" in data
    assert "server_time" in data


@pytest.mark.django_db
def test_sync_pull_filters_by_since(user):
    ContactFactory(owner=user, name="Old Contact")
    response = client.get("/sync/pull/?since=2099-01-01T00:00:00Z", user=user)
    assert response.status_code == 200
    assert response.json()["contacts"] == []


@pytest.mark.django_db
def test_sync_pull_requires_auth():
    response = client.get("/sync/pull/?since=2020-01-01T00:00:00Z")
    assert response.status_code == 401


@pytest.mark.django_db
def test_sync_push_create_contact(user):
    cid = str(uuid.uuid4())
    response = client.post(
        "/sync/push/",
        json={"changes": [{"entity": "contact", "operation": "create", "payload": {
            "id": cid, "name": "Sync Test", "context_tag": "work",
            "created_at": timezone.now().isoformat(),
        }}]},
        user=user,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["applied"]) == 1
    assert data["applied"][0]["id"] == cid


@pytest.mark.django_db
def test_sync_push_partial_success(user):
    cid = str(uuid.uuid4())
    response = client.post(
        "/sync/push/",
        json={"changes": [
            {"entity": "contact", "operation": "create", "payload": {
                "id": cid, "name": "Valid", "context_tag": "work",
                "created_at": timezone.now().isoformat(),
            }},
            {"entity": "interaction_entry", "operation": "create", "payload": {
                "id": str(uuid.uuid4()), "contact_id": str(uuid.uuid4()),  # unknown contact
                "content": "X", "created_at": timezone.now().isoformat(),
            }},
        ]},
        user=user,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["applied"]) == 1
    assert len(data["errors"]) == 1
