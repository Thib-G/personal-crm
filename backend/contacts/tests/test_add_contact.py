"""
T029 - Integration tests for adding a contact (US1).
"""
import uuid
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User

from crm.api import api
from contacts.models import Contact

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="tester", password="pass")


@pytest.mark.django_db
def test_contact_gps_stored_when_enabled(user):
    contact_id = str(uuid.uuid4())
    response = client.post(
        "/contacts/",
        json={
            "id": contact_id,
            "name": "GPS User",
            "context_tag": "event",
            "created_at": "2026-03-20T10:00:00Z",
            "created_lat": 48.8566,
            "created_lng": 2.3522,
        },
        user=user,
    )
    assert response.status_code == 201
    contact = Contact.objects.get(pk=contact_id)
    assert float(contact.created_lat) == pytest.approx(48.8566, abs=0.001)
    assert float(contact.created_lng) == pytest.approx(2.3522, abs=0.001)


@pytest.mark.django_db
def test_contact_gps_ignored_when_tracking_disabled(user):
    from settings_app.models import PrivacySettings
    ps = PrivacySettings.objects.get(user=user)
    ps.location_tracking_enabled = False
    ps.save()

    contact_id = str(uuid.uuid4())
    response = client.post(
        "/contacts/",
        json={
            "id": contact_id,
            "name": "No GPS User",
            "context_tag": "work",
            "created_at": "2026-03-20T10:00:00Z",
            "created_lat": 48.8566,
            "created_lng": 2.3522,
        },
        user=user,
    )
    assert response.status_code == 201
    contact = Contact.objects.get(pk=contact_id)
    assert contact.created_lat is None
    assert contact.created_lng is None


@pytest.mark.django_db
def test_blank_name_rejected(user):
    response = client.post(
        "/contacts/",
        json={"id": str(uuid.uuid4()), "name": "  ", "context_tag": "work", "created_at": "2026-03-20T10:00:00Z"},
        user=user,
    )
    assert response.status_code == 400
