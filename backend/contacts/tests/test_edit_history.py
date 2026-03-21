"""T047 - Integration tests for edit history (US3)."""
import uuid
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from crm.api import api
from contacts.tests.factories import ContactFactory, ContactPhoneFactory
from contacts.models import ContactHistory

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="histuser", password="pass")


@pytest.mark.django_db
def test_edit_name_creates_history(user):
    contact = ContactFactory(owner=user, name="Original")
    client.patch(f"/contacts/{contact.id}/", json={"name": "Changed"}, user=user)
    h = ContactHistory.objects.get(contact=contact, field_name="name")
    assert h.old_value == "Original"
    assert h.new_value == "Changed"


@pytest.mark.django_db
def test_history_visible_in_get_contact(user):
    contact = ContactFactory(owner=user, name="Before")
    client.patch(f"/contacts/{contact.id}/", json={"name": "After"}, user=user)
    response = client.get(f"/contacts/{contact.id}/", user=user)
    history = response.json()["history"]
    assert len(history) == 1
    assert history[0]["field_name"] == "name"
