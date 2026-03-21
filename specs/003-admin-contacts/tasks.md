# Tasks: Admin Contacts Management

**Input**: Design documents from `/specs/003-admin-contacts/`
**Prerequisites**: plan.md ✅ · spec.md ✅ · research.md ✅ · quickstart.md ✅

**Tests**: TDD is **MANDATORY** per Constitution Principle V. Test tasks appear before implementation tasks in every user story phase. Tests MUST fail before implementation begins.

**Organization**: Tasks are grouped by user story. All implementation lives in two files: `backend/contacts/admin.py` (new) and `backend/contacts/tests/test_admin.py` (new). No new models, no migrations.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel with other [P] tasks in the same phase (different files, no shared dependencies)
- **[Story]**: User story this task belongs to (US1–US3)

---

## Phase 1: Foundational

**Purpose**: Confirm the admin infrastructure is wired before writing any admin code.

- [X] T001 Verify `django.contrib.admin` is in `INSTALLED_APPS` and the admin URL (`path('admin/', admin.site.urls)`) is present in `backend/crm/urls.py`; confirm `python manage.py check` passes with no errors

**Checkpoint**: Admin URL resolves at `/admin/` — foundational check complete.

---

## Phase 2: User Story 1 — Browse and Search Contacts (Priority: P1) 🎯 MVP

**Goal**: The admin contacts list shows all contacts (including soft-deleted ones) with search by name/organisation and filters by context tag, owner, and deleted status.

**Independent Test**: Log in as superuser → open `/admin/contacts/contact/` → verify list renders with correct columns → search by name → apply context_tag filter → confirm soft-deleted contact appears.

### Tests (write FIRST — must FAIL before implementation)

- [X] T002 [US1] Write pytest tests for the ContactAdmin list view in `backend/contacts/tests/test_admin.py`: assert GET `/admin/contacts/contact/` returns 200; assert `name`, `owner`, `organisation`, `context_tag`, `is_deleted` appear in the response; assert a soft-deleted contact (is_deleted=True) appears in the list; assert search by name returns only matching contacts; assert `list_filter` sidebar is present for context_tag and is_deleted

### Implementation

- [X] T003 [US1] Implement `ContactAdmin` in `backend/contacts/admin.py`: register the `Contact` model; set `list_display = ('name', 'owner', 'organisation', 'context_tag', 'is_deleted', 'created_at')`; set `search_fields = ('name', 'organisation')`; set `list_filter = ('context_tag', 'owner', 'is_deleted')`; override `get_queryset()` to return `Contact.all_objects.all()` so soft-deleted records are visible (depends on T002)

**Checkpoint**: Run `pytest contacts/tests/test_admin.py -v` → T002 tests pass. Open admin contacts list → soft-deleted contacts visible with is_deleted indicator.

---

## Phase 3: User Story 2 — View and Edit Full Contact Details (Priority: P2)

**Goal**: The contact detail page in admin shows all fields and includes editable inline sections for phone numbers and email addresses.

**Independent Test**: Open any contact in admin → edit name → add a phone number inline → save → reopen → confirm changes persisted.

### Tests (write FIRST — must FAIL before implementation)

- [X] T004 [US2] Add tests to `backend/contacts/tests/test_admin.py` for the contact change view: assert GET `/admin/contacts/contact/<id>/change/` returns 200; assert phone number and email address inline sections are present in the response; assert a POST with a new phone number inline saves successfully and the phone appears on re-fetch (depends on T003)

### Implementation

- [X] T005 [US2] Add `ContactPhoneInline` (`TabularInline`, `model=ContactPhone`, `extra=1`, `can_delete=True`) and `ContactEmailInline` (`TabularInline`, `model=ContactEmail`, `extra=1`, `can_delete=True`) classes to `backend/contacts/admin.py`, and add both to `ContactAdmin.inlines` (depends on T004)

**Checkpoint**: Run `pytest contacts/tests/test_admin.py -v` → T004 tests pass. Open contact in admin → phones and emails editable inline.

---

## Phase 4: User Story 3 — Inspect Interaction and Change History (Priority: P3)

**Goal**: The contact detail page shows read-only inline sections for interaction entries and change history records, with no ability to add or edit entries.

**Independent Test**: Open a contact with interactions and history in admin → confirm both inline sections are visible → confirm no add/edit controls are present.

### Tests (write FIRST — must FAIL before implementation)

- [X] T006 [US3] Add tests to `backend/contacts/tests/test_admin.py` for read-only inlines: assert interaction entries and history records appear in the change view response for a contact that has them; assert no "add" management form row is present for interaction entries (max_num=0 check); assert no delete checkbox is rendered for history records (depends on T005)

### Implementation

- [X] T007 [US3] Add `InteractionEntryInline` (`TabularInline`, `model=InteractionEntry`, `extra=0`, `max_num=0`, `can_delete=False`, `readonly_fields=('content', 'created_at', 'lat', 'lng')`) and `ContactHistoryInline` (`TabularInline`, `model=ContactHistory`, `extra=0`, `max_num=0`, `can_delete=False`, `readonly_fields=('field_name', 'old_value', 'new_value', 'changed_at', 'lat', 'lng')`) to `backend/contacts/admin.py`, and add both to `ContactAdmin.inlines` (depends on T006)

**Checkpoint**: Run `pytest contacts/tests/test_admin.py -v` → all tests pass. Interactions and history visible read-only; no add/edit controls present.

---

## Phase 5: Polish & Validation

- [X] T008 Run `quickstart.md` validation end-to-end: verify all 3 scenarios (list+search, edit+inline phones/emails, read-only interactions/history), all edge cases (empty inlines, unauthenticated redirect)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundational)**: No dependencies — starts immediately
- **Phase 2 (US1)**: Depends on Phase 1
- **Phase 3 (US2)**: Depends on Phase 2 (ContactAdmin must exist before adding inlines)
- **Phase 4 (US3)**: Depends on Phase 3 (same file; inlines added incrementally)
- **Phase 5 (Polish)**: Depends on Phases 2–4

### User Story Dependencies

- **US1 (P1)**: Independent after foundational check
- **US2 (P2)**: Depends on US1 — inlines are added to the ContactAdmin created in US1
- **US3 (P3)**: Depends on US2 — further inlines added to the same ContactAdmin

### Within Each User Story

1. Write tests → confirm they FAIL (Red)
2. Implement admin class / inlines
3. Confirm tests PASS (Green)
4. Commit (one commit per task per Constitution Principle VI)

---

## Parallel Opportunities

All stories are sequential (single `admin.py` file, incremental additions). No parallel [P] opportunities within stories.

T001 (foundational check) can happen while reviewing the spec — it is a read-only verification.

---

## Implementation Strategy

### MVP (User Story 1 Only)

1. Complete Phase 1: Foundational (T001)
2. Complete Phase 2: US1 (T002–T003)
3. **STOP and VALIDATE**: Admin list works, search + filter + soft-deleted visibility confirmed
4. Ship — the list view is immediately useful for data lookup

### Full Feature

5. Complete Phase 3: US2 (T004–T005) — adds inline phones/emails
6. Complete Phase 4: US3 (T006–T007) — adds read-only interaction/history
7. Complete Phase 5: Polish (T008) — end-to-end validation

---

## Notes

- TDD is non-negotiable per Constitution Principle V. T002, T004, T006 must be written and confirmed failing before their implementation tasks begin.
- Each task = one atomic commit per Constitution Principle VI.
- No new npm packages, no new Python packages, no migrations.
- `Contact.all_objects` (the unfiltered manager) is the key to soft-delete visibility — do not use `Contact.objects` in `get_queryset()`.
