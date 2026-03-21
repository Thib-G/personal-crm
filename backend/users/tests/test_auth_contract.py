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
