# Implementation Plan: Admin Contacts Management

**Branch**: `003-admin-contacts` | **Date**: 2026-03-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-admin-contacts/spec.md`

## Summary

Register the existing `Contact`, `ContactPhone`, `ContactEmail`, `InteractionEntry`, and `ContactHistory` models with Django's built-in admin. The admin list shows all contacts including soft-deleted ones (via the unfiltered `all_objects` manager), with search by name/organisation, filters by context tag and owner. The contact detail page includes editable inline sections for phones and emails, and read-only inline sections for interactions and change history. No new models, no new dependencies, no frontend changes.

## Technical Context

**Language/Version**: Python 3.13
**Primary Dependencies**: Django 5.2 LTS (built-in `django.contrib.admin` — no new packages)
**Storage**: SQLite via Django ORM (no schema changes — no migrations needed)
**Testing**: pytest-django, factory-boy (already in use)
**Target Platform**: Django backend container
**Project Type**: Web application (backend admin UI)
**Performance Goals**: Standard Django admin response times (<1s for list views at single-user scale)
**Constraints**: No new dependencies (Constitution Technology & Stack Constraints); single-user scale
**Scale/Scope**: Single superuser accessing admin; all existing contacts in the database

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | ✓ PASS | Admin access is restricted to authenticated superusers via Django's built-in permission system. No contact data is exposed externally. |
| II. Simplicity Over Features | ✓ PASS | Uses only Django's built-in admin. Zero new dependencies. Two new files: `admin.py` and `test_admin.py`. |
| III. Data Integrity | ✓ PASS | Admin edits go through Django ORM with full model validation. No raw SQL. |
| IV. User-Owned Data | ✓ PASS | No new data structures; no change to export or delete behavior. |
| V. TDD | ✓ PASS | Test file written before `admin.py` implementation. Tests must fail before implementation begins. |
| VI. Atomic Commits | ✓ PASS | One commit per task (test file, admin.py per story, etc.). |

**Gate result**: All principles pass. No violations to justify.

## Project Structure

### Documentation (this feature)

```text
specs/003-admin-contacts/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── quickstart.md        ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit.tasks)
```

No `data-model.md` — no new entities. No `contracts/` — admin is a browser UI, not an API.

### Source Code (repository root)

```text
backend/
├── contacts/
│   ├── admin.py                          ← new (currently empty)
│   └── tests/
│       └── test_admin.py                 ← new
```

All other files are unchanged.

**Structure Decision**: Backend-only change. Admin registration lives in `contacts/admin.py` (the standard Django convention). Tests live alongside existing contact tests in `contacts/tests/`.

## Architecture

### `contacts/admin.py` — classes to implement

```text
ContactPhoneInline       TabularInline   editable    (extra=1, can_delete=True)
ContactEmailInline       TabularInline   editable    (extra=1, can_delete=True)
InteractionEntryInline   TabularInline   read-only   (max_num=0, can_delete=False, all readonly_fields)
ContactHistoryInline     TabularInline   read-only   (max_num=0, can_delete=False, all readonly_fields)
ContactAdmin             ModelAdmin      registered  (list_display, search_fields, list_filter,
                                                       get_queryset override → all_objects,
                                                       inlines: all four above)
```

### Key implementation details

- **Soft-delete visibility**: `ContactAdmin.get_queryset()` returns `Contact.all_objects.all()` — surfaces soft-deleted records without modifying the default manager used by the rest of the app.
- **Deleted indicator**: `is_deleted` added to `list_display`; list filter on `is_deleted` allows filtering to deleted-only records.
- **Read-only inlines**: `InteractionEntryInline` and `ContactHistoryInline` define `readonly_fields` covering all model fields, `extra = 0`, `max_num = 0`, `can_delete = False`.
- **No migrations**: This feature only registers existing models with the admin — zero schema changes.

## Complexity Tracking

No constitution violations. Table not required.
