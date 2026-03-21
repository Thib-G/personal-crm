"""T046 - Contract tests for DELETE /api/contacts/{id}/ (US3)."""
import uuid
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from crm.api import api
from contacts.tests.factories import ContactFactory
from contacts.models import Contact

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="deleter", password="pass")


@pytest.mark.django_db
def test_delete_contact_returns_204(user):
    contact = ContactFactory(owner=user)
    response = client.delete(f"/contacts/{contact.id}/", user=user)
    assert response.status_code == 204


@pytest.mark.django_db
def test_deleted_contact_not_in_list(user):
    contact = ContactFactory(owner=user)
    client.delete(f"/contacts/{contact.id}/", user=user)
    list_response = client.get("/contacts/", user=user)
    ids = [c["id"] for c in list_response.json()]
    assert str(contact.id) not in ids


@pytest.mark.django_db
def test_deleted_contact_get_returns_404(user):
    contact = ContactFactory(owner=user)
    client.delete(f"/contacts/{contact.id}/", user=user)
    response = client.get(f"/contacts/{contact.id}/", user=user)
    assert response.status_code == 404


@pytest.mark.django_db
def test_delete_sets_soft_delete_flag(user):
    contact = ContactFactory(owner=user)
    client.delete(f"/contacts/{contact.id}/", user=user)
    deleted = Contact.all_objects.get(pk=contact.id)
    assert deleted.is_deleted is True
    assert deleted.deleted_at is not None
