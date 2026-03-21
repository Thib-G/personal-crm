"""T045 - Contract tests for PATCH /api/contacts/{id}/ (US3)."""
import uuid
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from crm.api import api
from contacts.tests.factories import ContactFactory
from contacts.models import ContactHistory

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="editor", password="pass")


@pytest.mark.django_db
def test_patch_contact_name(user):
    contact = ContactFactory(owner=user, name="Old Name")
    response = client.patch(
        f"/contacts/{contact.id}/",
        json={"name": "New Name", "edit_lat": 50.85, "edit_lng": 4.35},
        user=user,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"
    history = ContactHistory.objects.filter(contact=contact)
    assert history.count() == 1
    assert history.first().old_value == "Old Name"
    assert history.first().new_value == "New Name"


@pytest.mark.django_db
def test_patch_records_gps_in_history(user):
    contact = ContactFactory(owner=user, name="Test")
    client.patch(
        f"/contacts/{contact.id}/",
        json={"name": "Updated", "edit_lat": 48.85, "edit_lng": 2.35},
        user=user,
    )
    h = ContactHistory.objects.get(contact=contact)
    assert float(h.lat) == pytest.approx(48.85, abs=0.01)


@pytest.mark.django_db
def test_patch_blank_name_rejected(user):
    contact = ContactFactory(owner=user, name="Valid")
    response = client.patch(f"/contacts/{contact.id}/", json={"name": ""}, user=user)
    assert response.status_code == 400


@pytest.mark.django_db
def test_patch_not_found(user):
    response = client.patch(f"/contacts/{uuid.uuid4()}/", json={"name": "X"}, user=user)
    assert response.status_code == 404
