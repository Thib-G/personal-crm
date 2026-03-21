"""
T013 - Integration tests for auth session flow.
"""
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User

from crm.api import api

client = TestClient(api)


@pytest.mark.django_db
def test_unauthenticated_contacts_returns_401(db):
    response = client.get("/contacts/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_authenticated_contacts_returns_200(db):
    user = User.objects.create_user(username="charlie", password="pass")
    response = client.get("/contacts/", user=user)
    assert response.status_code == 200


@pytest.mark.django_db
def test_privacy_settings_auto_created_on_user_creation(db):
    from settings_app.models import PrivacySettings
    user = User.objects.create_user(username="dave", password="pass")
    assert PrivacySettings.objects.filter(user=user).exists()
    settings = PrivacySettings.objects.get(user=user)
    assert settings.location_tracking_enabled is True
