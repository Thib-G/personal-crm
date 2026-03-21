"""T038 - Contract tests for GET /api/contacts/ (US2)."""
import uuid
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from crm.api import api
from contacts.tests.factories import ContactFactory, ContactPhoneFactory, InteractionEntryFactory

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="tester", password="pass")


@pytest.mark.django_db
def test_list_contacts_returns_200(user):
    response = client.get("/contacts/", user=user)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.django_db
def test_list_contacts_requires_auth():
    response = client.get("/contacts/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_search_by_name(user):
    ContactFactory(owner=user, name="Alice Dupont")
    ContactFactory(owner=user, name="Bob Martin")
    response = client.get("/contacts/?q=alice", user=user)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Alice Dupont"


@pytest.mark.django_db
def test_search_min_length(user):
    response = client.get("/contacts/?q=a", user=user)
    assert response.status_code == 400


@pytest.mark.django_db
def test_search_empty_returns_all(user):
    ContactFactory(owner=user, name="Alice")
    ContactFactory(owner=user, name="Bob")
    response = client.get("/contacts/", user=user)
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.django_db
def test_search_across_interaction_entries(user):
    contact = ContactFactory(owner=user, name="Carol")
    InteractionEntryFactory(contact=contact, content="discussed the quarterly report")
    response = client.get("/contacts/?q=quarterly", user=user)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.django_db
def test_search_across_phone(user):
    contact = ContactFactory(owner=user, name="Dave")
    ContactPhoneFactory(contact=contact, number="+32491234567")
    response = client.get("/contacts/?q=3249123", user=user)
    assert response.status_code == 200
    assert len(response.json()) == 1
