"""T076 - Contract tests for GET /api/contacts/map/pins/ (US6)."""
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from django.utils import timezone
from crm.api import api
from contacts.tests.factories import ContactFactory, InteractionEntryFactory

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="mapuser", password="pass")


@pytest.mark.django_db
def test_map_pins_returns_200(user):
    response = client.get("/contacts/map/pins/", user=user)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db
def test_map_pins_includes_contact_with_gps(user):
    ContactFactory(owner=user, name="Alice", created_lat=50.85, created_lng=4.35)
    response = client.get("/contacts/map/pins/", user=user)
    pins = response.json()
    assert len(pins) == 1
    assert pins[0]["type"] == "contact"
    assert pins[0]["contact_name"] == "Alice"


@pytest.mark.django_db
def test_map_pins_excludes_contact_without_gps(user):
    ContactFactory(owner=user, name="No GPS", created_lat=None, created_lng=None)
    response = client.get("/contacts/map/pins/", user=user)
    assert response.json() == []


@pytest.mark.django_db
def test_map_pins_includes_interaction_with_gps(user):
    contact = ContactFactory(owner=user, name="Bob")
    InteractionEntryFactory(contact=contact, content="Meeting in Brussels", lat=50.85, lng=4.35)
    response = client.get("/contacts/map/pins/", user=user)
    pins = [p for p in response.json() if p["type"] == "interaction"]
    assert len(pins) == 1


@pytest.mark.django_db
def test_map_pins_requires_auth():
    response = client.get("/contacts/map/pins/")
    assert response.status_code == 401
