# Quickstart & Validation: Admin Contacts Management

**Feature**: 003-admin-contacts
**Date**: 2026-03-21

---

## Prerequisites

- Dev stack running: `docker compose -f docker-compose.dev.yml up`
- A superuser account exists (create with `python manage.py createsuperuser` if needed)
- At least one contact with phones, emails, an interaction entry, and change history exists

---

## Scenario 1: Browse and Search Contacts (US1)

1. Open `http://localhost:8000/admin/` and log in as superuser.
2. Click **Contacts → Contacts**.
3. **Verify**: Paginated list shows all contacts with columns: Name, Owner, Organisation, Context Tag, Created At.
4. **Verify**: Soft-deleted contacts appear in the list with a clear visual indicator (e.g., strikethrough or "deleted" badge).
5. Type a partial name in the search box and press Enter.
6. **Verify**: Only contacts matching the name or organisation are shown.
7. Use the **Context tag** filter sidebar to select "work".
8. **Verify**: Only contacts with `context_tag = work` are shown.
9. Use the **Owner** filter to select a specific user.
10. **Verify**: Only that user's contacts are shown.

---

## Scenario 2: Edit Contact with Inline Phones and Emails (US2)

1. From the contacts list, click on any contact.
2. **Verify**: Detail page shows all fields: Name, Organisation, Context Tag, Created At, coordinates (lat/lng).
3. **Verify**: Phone numbers section appears inline — existing numbers are shown; there is one empty row to add a new number.
4. **Verify**: Email addresses section appears inline — same structure.
5. Edit the contact's name, add a phone number in the inline, and click **Save**.
6. **Verify**: Returns to the list. The updated name is visible.
7. Re-open the contact.
8. **Verify**: The new phone number appears in the inline list.
9. Delete the phone number (tick the delete checkbox) and save.
10. **Verify**: The phone number is gone on re-open.

---

## Scenario 3: Inspect Read-Only Interaction and Change History (US3)

1. Open a contact that has at least one interaction entry and one history record.
2. **Verify**: Interaction entries section is visible inline — shows content and date.
3. **Verify**: No "Add another interaction" row exists and no edit controls are present (fields are displayed as plain text).
4. **Verify**: Change history section is visible inline — shows field name, old value, new value, and timestamp.
5. **Verify**: No "Add another history" row and no edit controls exist.

---

## Automated Test Validation

Run the admin-specific tests:

```bash
docker compose -f docker-compose.dev.yml exec backend pytest contacts/tests/test_admin.py -v
```

Expected: all tests pass (GREEN).

---

## Edge Case Checks

- Open a contact with **no phones and no emails**: inline sections show zero rows with no errors.
- Open a contact with **no interaction entries**: interaction inline shows empty with no errors.
- Attempt to access `/admin/contacts/contact/` without being logged in: redirected to admin login page.
