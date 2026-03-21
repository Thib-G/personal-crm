"""T070 - Integration tests for GPS privacy enforcement (US5)."""
import uuid
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from django.utils import timezone
from crm.api import api
from contacts.models import Contact

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="privint", password="pass")


@pytest.mark.django_db
def test_disable_gps_prevents_location_on_contact_create(user):
    client.patch("/settings/privacy/", json={"location_tracking_enabled": False}, user=user)
    cid = str(uuid.uuid4())
    client.post(
        "/contacts/",
        json={"id": cid, "name": "No GPS", "context_tag": "work", "created_at": timezone.now().isoformat(), "created_lat": 50.0, "created_lng": 4.0},
        user=user,
    )
    contact = Contact.all_objects.get(pk=cid)
    assert contact.created_lat is None
