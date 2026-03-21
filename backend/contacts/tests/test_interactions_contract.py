"""T058/T059 - Contract tests for interaction entries (US4)."""
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
    return User.objects.create_user(username="interact", password="pass")


@pytest.mark.django_db
def test_add_interaction_success(user):
    contact = ContactFactory(owner=user)
    response = client.post(
        f"/contacts/{contact.id}/interactions/",
        json={
            "id": str(uuid.uuid4()),
            "content": "Had a great meeting",
            "created_at": timezone.now().isoformat(),
            "lat": 50.85,
            "lng": 4.35,
        },
        user=user,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Had a great meeting"
    assert data["lat"] == pytest.approx(50.85, abs=0.01)


@pytest.mark.django_db
def test_add_interaction_blank_content(user):
    contact = ContactFactory(owner=user)
    response = client.post(
        f"/contacts/{contact.id}/interactions/",
        json={"id": str(uuid.uuid4()), "content": "", "created_at": timezone.now().isoformat()},
        user=user,
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_add_interaction_requires_auth():
    response = client.post(
        f"/contacts/{uuid.uuid4()}/interactions/",
        json={"id": str(uuid.uuid4()), "content": "X", "created_at": timezone.now().isoformat()},
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_add_interaction_unknown_contact(user):
    response = client.post(
        f"/contacts/{uuid.uuid4()}/interactions/",
        json={"id": str(uuid.uuid4()), "content": "X", "created_at": timezone.now().isoformat()},
        user=user,
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_list_interactions_newest_first(user):
    contact = ContactFactory(owner=user)
    from datetime import datetime, timedelta, timezone as dt_tz
    t1 = datetime(2026, 1, 1, 10, 0, tzinfo=dt_tz.utc)
    t2 = datetime(2026, 1, 1, 11, 0, tzinfo=dt_tz.utc)
    InteractionEntryFactory(contact=contact, content="First", created_at=t1)
    InteractionEntryFactory(contact=contact, content="Second", created_at=t2)
    response = client.get(f"/contacts/{contact.id}/interactions/", user=user)
    assert response.status_code == 200
    data = response.json()
    assert data[0]["content"] == "Second"
    assert data[1]["content"] == "First"
