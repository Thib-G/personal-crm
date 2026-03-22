"""
T012 - Contract tests for auth endpoints.
"""
import pytest
from ninja.testing import TestClient
from django.contrib.auth.models import User
from django.test import Client as DjangoClient

from crm.api import api

ninja_client = TestClient(api)


@pytest.mark.django_db
def test_login_success():
    User.objects.create_user(username="alice", password="secret123")
    # Use Django test client for session-based login
    c = DjangoClient()
    response = c.post(
        "/api/auth/login/",
        data='{"username": "alice", "password": "secret123"}',
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "alice"
    assert "id" in data


@pytest.mark.django_db
def test_login_invalid_credentials():
    c = DjangoClient()
    response = c.post(
        "/api/auth/login/",
        data='{"username": "nobody", "password": "wrong"}',
        content_type="application/json",
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_me_requires_auth():
    response = ninja_client.get("/auth/me/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_me_returns_authenticated_user():
    user = User.objects.create_user(username="bob", password="secret123")
    response = ninja_client.get("/auth/me/", user=user)
    assert response.status_code == 200
    assert response.json()["username"] == "bob"


@pytest.mark.django_db
def test_logout_without_session_returns_200():
    """Logout must be callable with no active session (auth=None contract)."""
    c = DjangoClient()
    response = c.post("/api/auth/logout/")
    assert response.status_code == 200
    assert response.json()["detail"] == "Logged out"


@pytest.mark.django_db
def test_logout_with_session_invalidates_it():
    """After logout, the session must be invalidated — /api/auth/me/ returns 401."""
    User.objects.create_user(username="carol", password="secret123")
    c = DjangoClient()
    c.post(
        "/api/auth/login/",
        data='{"username": "carol", "password": "secret123"}',
        content_type="application/json",
    )
    # Confirm authenticated
    assert c.get("/api/auth/me/").status_code == 200
    # Logout
    logout_response = c.post("/api/auth/logout/")
    assert logout_response.status_code == 200
    # Session must be gone
    assert c.get("/api/auth/me/").status_code == 401
