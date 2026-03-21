# Research: Admin Contacts Management

**Feature**: 003-admin-contacts
**Date**: 2026-03-21

---

## Decision 1: Soft-deleted contact visibility in admin list

**Decision**: Override `get_queryset()` on `ContactAdmin` to use `Contact.all_objects` (the unfiltered manager).

**Rationale**: `Contact.objects` is an `ActiveContactManager` that silently filters `is_deleted=True`. If left as-is, the Django admin would inherit this default manager and hide soft-deleted contacts entirely — violating FR-004. Overriding `get_queryset()` with `Contact.all_objects.all()` surfaces all records. A custom `is_deleted` column and list filter are then added to distinguish deleted from active contacts visually.

**Alternatives considered**:
- Using a separate `DeletedContactAdmin` with a custom queryset: rejected — two admin registrations for one model adds unnecessary complexity (Principle II).
- Removing the default manager filter entirely: rejected — the app's sync API depends on `Contact.objects` filtering out deleted records.

---

## Decision 2: Read-only inlines for InteractionEntry and ContactHistory

**Decision**: Use `TabularInline` subclasses with all fields listed in `readonly_fields`, `extra = 0`, `can_delete = False`, and `max_num = 0`.

**Rationale**: Setting `max_num = 0` prevents adding new rows. Setting `can_delete = False` removes delete checkboxes. Listing all fields in `readonly_fields` renders them as static text. This is the standard Django pattern for display-only inlines with zero implementation overhead.

**Alternatives considered**:
- Custom `InlineModelAdmin` with `has_add_permission` / `has_delete_permission` returning `False`: valid alternative, but `max_num = 0` + `can_delete = False` achieves the same result with fewer lines.
- Separate detail pages for interactions/history: rejected — the spec requires them on the contact page with no additional navigation (SC-004).

---

## Decision 3: Editable inlines for ContactPhone and ContactEmail

**Decision**: Standard `TabularInline` with `extra = 1` (one blank row for adding), `can_delete = True`.

**Rationale**: This is the simplest Django inline pattern. It supports add, edit, and delete inline — satisfying FR-007 and FR-008 with no custom code.

**Alternatives considered**:
- `StackedInline`: works identically but takes more vertical space for simple two-field models. `TabularInline` is more compact.

---

## Decision 4: Test strategy

**Decision**: Use pytest-django with `django.test.Client` (force-logged-in superuser). Test the admin list URL, change URL, and search/filter parameters directly via HTTP GET/POST assertions.

**Rationale**: Django admin views are standard HTTP views. Testing them via the client exercises the full stack (URL routing → ModelAdmin → queryset → template rendering) without mocking. The existing test suite already uses pytest-django and factory-boy — no new tools needed.

**Alternatives considered**:
- Selenium / browser-based tests: overkill for admin UI; adds a heavy dependency (Principle II).
- Unit-testing `ModelAdmin` methods directly: misses URL routing and permission checks; integration tests via client are more valuable.

---

## Decision 5: No new dependencies

**Decision**: This feature uses only Django's built-in admin machinery (`django.contrib.admin`). Zero new packages.

**Rationale**: Django admin ships with all required capabilities: list display, search, filters, inlines, read-only fields, queryset override. Adding a third-party admin framework (django-grappelli, etc.) would violate Principle II and the constitution's dependency-minimization requirement.
