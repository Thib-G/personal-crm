"""T077 - Map integration tests (US6)."""
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from crm.api import api
from contacts.tests.factories import ContactFactory, InteractionEntryFactory

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="mapint", password="pass")


@pytest.mark.django_db
def test_map_pins_count(user):
    ContactFactory(owner=user, created_lat=50.85, created_lng=4.35)
    ContactFactory(owner=user, created_lat=48.85, created_lng=2.35)
    ContactFactory(owner=user, created_lat=None, created_lng=None)  # no GPS
    contact = ContactFactory(owner=user)
    InteractionEntryFactory(contact=contact, lat=51.50, lng=-0.12)
    InteractionEntryFactory(contact=contact, lat=52.37, lng=4.90)

    response = client.get("/contacts/map/pins/", user=user)
    pins = response.json()
    # 2 contacts with GPS + 2 interactions with GPS = 4
    assert len(pins) == 4
