"""T069 - Contract tests for privacy settings (US5)."""
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from crm.api import api

client = TestClient(api)


@pytest.fixture
def user(db):
    return User.objects.create_user(username="privuser", password="pass")


@pytest.mark.django_db
def test_get_privacy_settings(user):
    response = client.get("/settings/privacy/", user=user)
    assert response.status_code == 200
    assert response.json()["location_tracking_enabled"] is True


@pytest.mark.django_db
def test_patch_privacy_settings(user):
    response = client.patch("/settings/privacy/", json={"location_tracking_enabled": False}, user=user)
    assert response.status_code == 200
    assert response.json()["location_tracking_enabled"] is False


@pytest.mark.django_db
def test_privacy_settings_require_auth():
    response = client.get("/settings/privacy/")
    assert response.status_code == 401
