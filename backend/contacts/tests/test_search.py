"""T039 - Search integration tests (US2)."""
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from crm.api import api
from contacts.tests.factories import ContactFactory, ContactEmailFactory

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="searcher", password="pass")


@pytest.mark.django_db
def test_search_returns_empty_list_when_no_match(user):
    ContactFactory(owner=user, name="Zara")
    response = client.get("/contacts/?q=xyz_no_match", user=user)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.django_db
def test_search_across_email(user):
    contact = ContactFactory(owner=user, name="Eve")
    ContactEmailFactory(contact=contact, address="eve@startup.io")
    response = client.get("/contacts/?q=startup", user=user)
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.django_db
def test_search_across_organisation(user):
    ContactFactory(owner=user, name="Frank", organisation="DeepTech SPRL")
    response = client.get("/contacts/?q=deeptech", user=user)
    assert response.status_code == 200
    assert len(response.json()) == 1
