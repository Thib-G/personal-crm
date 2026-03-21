"""T060 - Interaction integration tests (US4)."""
import uuid
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from django.utils import timezone
from crm.api import api
from contacts.tests.factories import ContactFactory
from contacts.models import InteractionEntry

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="intuser", password="pass")


@pytest.mark.django_db
def test_interaction_gps_ignored_when_tracking_disabled(user):
    from settings_app.models import PrivacySettings
    ps = PrivacySettings.objects.get(user=user)
    ps.location_tracking_enabled = False
    ps.save()

    contact = ContactFactory(owner=user)
    entry_id = str(uuid.uuid4())
    response = client.post(
        f"/contacts/{contact.id}/interactions/",
        json={"id": entry_id, "content": "Meeting", "created_at": timezone.now().isoformat(), "lat": 50.85, "lng": 4.35},
        user=user,
    )
    assert response.status_code == 201
    entry = InteractionEntry.objects.get(pk=entry_id)
    assert entry.lat is None
