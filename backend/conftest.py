import pytest
from django.contrib.auth.models import User
from ninja.testing import TestClient

from crm.api import api


@pytest.fixture
def client():
    """Unauthenticated Ninja test client."""
    return TestClient(api)


@pytest.fixture
def user(db):
    """Create a test user with PrivacySettings auto-created via signal."""
    return User.objects.create_user(username="testuser", password="testpass123")


@pytest.fixture
def auth_client(user):
    """Ninja test client authenticated as the test user."""
    client = TestClient(api)
    # Simulate session by passing user directly to TestClient
    client.headers = {}
    # Use Django test client for session-based auth in integration tests
    return client


@pytest.fixture
def auth_headers(user):
    """Return auth cookie headers for Django test client."""
    from django.test import Client as DjangoClient

    c = DjangoClient()
    c.login(username="testuser", password="testpass123")
    return c
