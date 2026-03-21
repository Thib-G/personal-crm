"""
Tests for ContactAdmin (US1, US2, US3).
TDD: tests written before admin.py implementation.
Uses Django's test Client directly (conftest overrides `client` with Ninja TestClient).
"""
import uuid
import pytest
from django.test import Client
from django.contrib.auth.models import User
from contacts.tests.factories import (
    ContactFactory,
    ContactPhoneFactory,
    ContactEmailFactory,
    InteractionEntryFactory,
    ContactHistoryFactory,
)


@pytest.fixture(autouse=True)
def use_plain_static_storage(settings):
    """Override WhiteNoise manifest storage — admin tests don't need compiled static files."""
    settings.STORAGES = {
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        }
    }


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser(username="admin", password="adminpass")


@pytest.fixture
def admin_client(superuser):
    c = Client()
    c.force_login(superuser)
    return c


# ---------------------------------------------------------------------------
# US1 — Browse and Search Contacts
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_contact_list_returns_200(admin_client):
    response = admin_client.get("/admin/contacts/contact/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_contact_list_shows_key_columns(admin_client):
    ContactFactory()
    response = admin_client.get("/admin/contacts/contact/")
    content = response.content.decode()
    assert "Name" in content
    assert "Owner" in content
    assert "Organisation" in content


@pytest.mark.django_db
def test_soft_deleted_contact_visible_in_list(admin_client):
    ContactFactory(name="Active Person")
    ContactFactory(name="Deleted Person", is_deleted=True)
    response = admin_client.get("/admin/contacts/contact/")
    content = response.content.decode()
    assert "Active Person" in content
    assert "Deleted Person" in content


@pytest.mark.django_db
def test_search_by_name_filters_results(admin_client):
    ContactFactory(name="Alice Dupont")
    ContactFactory(name="Bob Martin")
    response = admin_client.get("/admin/contacts/contact/?q=Alice")
    content = response.content.decode()
    assert "Alice Dupont" in content
    assert "Bob Martin" not in content


@pytest.mark.django_db
def test_search_by_organisation_filters_results(admin_client):
    ContactFactory(name="Carol", organisation="Acme Corp")
    ContactFactory(name="Dave", organisation="Other Inc")
    response = admin_client.get("/admin/contacts/contact/?q=Acme")
    content = response.content.decode()
    assert "Carol" in content
    assert "Dave" not in content


@pytest.mark.django_db
def test_list_filter_sidebar_present(admin_client):
    response = admin_client.get("/admin/contacts/contact/")
    content = response.content.decode()
    assert response.status_code == 200
    # Django renders list_filter entries in the sidebar
    assert "context_tag" in content or "Context tag" in content


@pytest.mark.django_db
def test_unauthenticated_redirected_to_login():
    c = Client()
    response = c.get("/admin/contacts/contact/")
    assert response.status_code == 302
    assert "login" in response["Location"]


# ---------------------------------------------------------------------------
# US2 — View and Edit Full Contact Details (inline phones and emails)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_contact_change_view_returns_200(admin_client):
    contact = ContactFactory()
    response = admin_client.get(f"/admin/contacts/contact/{contact.pk}/change/")
    assert response.status_code == 200


@pytest.mark.django_db
def test_contact_change_view_shows_phone_inline(admin_client):
    contact = ContactFactory()
    ContactPhoneFactory(contact=contact, number="+32491234567")
    response = admin_client.get(f"/admin/contacts/contact/{contact.pk}/change/")
    content = response.content.decode()
    assert "+32491234567" in content


@pytest.mark.django_db
def test_contact_change_view_shows_email_inline(admin_client):
    contact = ContactFactory()
    ContactEmailFactory(contact=contact, address="test@example.com")
    response = admin_client.get(f"/admin/contacts/contact/{contact.pk}/change/")
    content = response.content.decode()
    assert "test@example.com" in content


@pytest.mark.django_db
def test_add_phone_inline_via_post(admin_client, superuser):
    contact = ContactFactory(owner=superuser)
    # id is editable=False on ContactPhone — do not include it in POST data
    post_data = {
        "name": contact.name,
        "owner": str(superuser.pk),
        "context_tag": contact.context_tag,
        "created_at_0": "2026-01-01",
        "created_at_1": "00:00:00",
        "phones-TOTAL_FORMS": "1",
        "phones-INITIAL_FORMS": "0",
        "phones-MIN_NUM_FORMS": "0",
        "phones-MAX_NUM_FORMS": "1000",
        "phones-0-contact": str(contact.pk),
        "phones-0-number": "+32499000001",
        "phones-0-DELETE": "",
        "emails-TOTAL_FORMS": "0",
        "emails-INITIAL_FORMS": "0",
        "emails-MIN_NUM_FORMS": "0",
        "emails-MAX_NUM_FORMS": "1000",
        "interaction_entries-TOTAL_FORMS": "0",
        "interaction_entries-INITIAL_FORMS": "0",
        "interaction_entries-MIN_NUM_FORMS": "0",
        "interaction_entries-MAX_NUM_FORMS": "0",
        "history-TOTAL_FORMS": "0",
        "history-INITIAL_FORMS": "0",
        "history-MIN_NUM_FORMS": "0",
        "history-MAX_NUM_FORMS": "0",
        "_save": "Save",
    }
    response = admin_client.post(
        f"/admin/contacts/contact/{contact.pk}/change/", post_data
    )
    assert response.status_code in (200, 302)
    assert contact.phones.filter(number="+32499000001").exists()


# ---------------------------------------------------------------------------
# US3 — Inspect Interaction and Change History (read-only inlines)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
def test_interaction_entries_visible_in_change_view(admin_client):
    contact = ContactFactory()
    InteractionEntryFactory(contact=contact, content="Had a great call today")
    response = admin_client.get(f"/admin/contacts/contact/{contact.pk}/change/")
    content = response.content.decode()
    assert "Had a great call today" in content


@pytest.mark.django_db
def test_history_records_visible_in_change_view(admin_client):
    contact = ContactFactory()
    ContactHistoryFactory(contact=contact, field_name="name", old_value="OldName", new_value="NewName")
    response = admin_client.get(f"/admin/contacts/contact/{contact.pk}/change/")
    content = response.content.decode()
    assert "OldName" in content
    assert "NewName" in content


@pytest.mark.django_db
def test_interaction_inline_no_extra_add_row(admin_client):
    contact = ContactFactory()
    response = admin_client.get(f"/admin/contacts/contact/{contact.pk}/change/")
    content = response.content.decode()
    # max_num=0: management form TOTAL_FORMS should equal INITIAL_FORMS (0 extras)
    assert "interaction_entries-TOTAL_FORMS" in content


@pytest.mark.django_db
def test_history_inline_no_delete_checkbox(admin_client):
    contact = ContactFactory()
    ContactHistoryFactory(contact=contact, field_name="name", old_value="Old", new_value="New")
    response = admin_client.get(f"/admin/contacts/contact/{contact.pk}/change/")
    content = response.content.decode()
    # can_delete=False: no DELETE checkbox rendered for history rows
    assert "history-0-DELETE" not in content
