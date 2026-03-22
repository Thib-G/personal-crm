---
description: "Task list for 006-fix-sync-ui-refresh"
---

# Tasks: Fix Sync — UI Does Not Reflect Data Changes Without Page Reload

**Input**: Design documents from `/specs/006-fix-sync-ui-refresh/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, contracts/ ✅

**Tests**: TDD is MANDATORY per constitution. Test tasks appear before their corresponding implementation tasks in each phase. Tests must be written first and must fail before implementation begins.

**Organization**: Tasks grouped by user story. US1 and US3 share the same data layer (stores); US2 (detail page) and US4 (sync button) are independent and can proceed in parallel after foundational work.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to

---

## Phase 1: Setup

No new packages or project structure changes required. `liveQuery` is already exported by the installed `dexie` package.

- [x] T001 Verify `liveQuery` is exported by the installed dexie version: read `frontend/package.json` to confirm dexie ≥ 3.x is installed (liveQuery was added in 3.0), and confirm the import `import { liveQuery } from 'dexie'` resolves in `frontend/src/services/db.ts` without errors

**Checkpoint**: Confirmed that `liveQuery` is available with no new installs needed.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Expose `syncNow()` publicly before any user story work that depends on it.

**⚠️ CRITICAL**: US4 (Sync Now button) cannot be implemented until this phase is complete.

- [x] T002 Expose `syncCycle()` as a public `syncNow()` method on `SyncService` in `frontend/src/services/sync.ts` — add `syncNow(): Promise<void> { return this.syncCycle() }` as a public method so the button component can call it without reaching into private internals

**Checkpoint**: `syncService.syncNow()` is callable from outside `sync.ts`.

---

## Phase 3: User Story 1 — Contact List Stays Current After Sync (Priority: P1) 🎯 MVP

**Goal**: `ContactListPage` reflects any write to `db.contacts` automatically, without `loadContacts()` being called explicitly.

**Independent Test**: Mock a direct `db.contacts.put()` call (simulating a sync pull) and assert that `contactStore.contacts` updates reactively without any store action being called.

### Tests for User Story 1

> **Write these tests FIRST — they must FAIL before T004 is implemented**

- [x] T003 [US1] Write a failing test in `frontend/src/pages/tests/ContactList.spec.ts` that asserts `contactStore.contacts` is populated via `liveQuery` reactivity (not `loadContacts()`): mock `liveQuery` from `dexie` to emit a predefined contact list and verify the component renders those contacts without `loadContacts()` being called

### Implementation for User Story 1

- [x] T004 [US1] Migrate `frontend/src/stores/contacts.ts` to use `liveQuery`: (a) import `liveQuery` from `dexie`; (b) start a `liveQuery(() => db.contacts.orderBy('name').toArray().then(all => all.filter(c => !c.is_deleted)))` subscription at store init that writes to `contacts`; (c) convert `loadContacts()` to a no-op (keep signature for call-site compatibility); (d) remove the `await loadContacts()` tail calls from `createContact`, `updateContact`, and `deleteContact`
- [x] T005 [US1] Update the `dexie` mock in `frontend/src/pages/tests/ContactList.spec.ts` to also mock `liveQuery` as `vi.fn(() => ({ subscribe: vi.fn(() => ({ unsubscribe: vi.fn() })) }))` so existing tests continue to pass after the store migration

**Checkpoint**: Contact list renders correctly, existing tests pass, and the liveQuery reactivity test (T003) now passes.

---

## Phase 4: User Story 2 — Contact Detail View Stays Current After Sync (Priority: P2)

**Goal**: `ContactDetailPage` reflects writes to `db.contacts`, `db.contact_phones`, `db.contact_emails`, and `db.contact_history` for the current contact ID automatically.

**Independent Test**: Mount `ContactDetailPage`, simulate a direct `db.contacts.update()` call for the displayed contact, and assert the page re-renders with the new field values without any explicit reload.

### Tests for User Story 2

> **Write these tests FIRST — they must FAIL before T007 is implemented**

- [x] T006 [P] [US2] Write failing tests in `frontend/src/pages/tests/ContactDetail.spec.ts` (new file): (a) test that contact data is displayed from the `liveQuery` emission; (b) test that `loading` is `false` after the first emission; (c) test that phones and emails from `liveQuery` emissions are rendered; mock `liveQuery` from `dexie` and `db` from `@/services/db`

### Implementation for User Story 2

- [x] T007 [US2] Replace the `loadContact()` function and the 4 one-off `db.xxx.get/where` reads in `frontend/src/pages/ContactDetailPage.vue` with 4 `liveQuery` subscriptions (one each for contact, phones, emails, history), all scoped to `id`; set `loading.value = false` on the first contact subscription emission; unsubscribe all 4 in `onUnmounted`

**Checkpoint**: Contact detail page renders reactively; T006 tests pass; no navigation required to see sync-pulled updates.

---

## Phase 5: User Story 3 — Interaction Feed Stays Current After Sync (Priority: P3)

**Goal**: `InteractionFeed` reflects writes to `db.interaction_entries` for the current contact automatically.

**Independent Test**: Mount `InteractionFeed`, simulate a direct `db.interaction_entries.add()` call for the current contact, and assert the new entry appears without `loadForContact()` being called.

### Tests for User Story 3

> **Write these tests FIRST — they must FAIL before T009 is implemented**

- [x] T008 [P] [US3] Write failing tests in `frontend/src/components/tests/InteractionFeed.spec.ts` (new file): (a) test that entries are rendered from `liveQuery` emission; (b) test that changing `contactId` prop causes a new subscription scoped to the new ID; mock `liveQuery` from `dexie` and `@/stores/interactions`

### Implementation for User Story 3

- [x] T009 [US3] Migrate `frontend/src/stores/interactions.ts` to use `liveQuery`: (a) import `liveQuery` from `dexie` and `watch` from `vue`; (b) create a `liveQuery` subscription scoped to `currentContactId.value` that writes to `entries`; (c) use `watch(currentContactId, ...)` to unsubscribe the old query and start a new one when the contact changes; (d) keep `loadForContact()` to set `currentContactId` and trigger the watch, but remove the manual DB read from it

**Checkpoint**: Interaction feed updates reactively; T008 tests pass.

---

## Phase 6: User Story 4 — User Manually Triggers a Sync (Priority: P2)

**Goal**: A "Sync Now" button in the nav bar calls `syncService.syncNow()` when clicked, is disabled while syncing or offline, and is accessible from every page.

**Independent Test**: Mount `SyncNowButton`, set each of the 4 `syncStatus` values, assert disabled/enabled state and that clicking the enabled states calls `syncNow()`.

### Tests for User Story 4

> **Write these tests FIRST — they must FAIL before T011 is implemented**

- [x] T010 [P] [US4] Write failing tests in `frontend/src/components/tests/SyncNowButton.spec.ts` (new file) covering all 4 states from `specs/006-fix-sync-ui-refresh/contracts/sync-now-button.md`: (a) `synced` → button enabled, click calls `syncService.syncNow()`; (b) `syncing` → button has `disabled` attribute, click does not call `syncNow()`; (c) `offline` → button has `disabled` attribute; (d) `error` → button enabled, click calls `syncNow()`; mock `@/services/sync` with `mockSyncStatus` and `syncService: { syncNow: vi.fn() }`

### Implementation for User Story 4

- [x] T011 [US4] Create `frontend/src/components/SyncNowButton.vue`: a `<button type="button" aria-label="Sync now">` that reads `syncStatus` from `@/services/sync`, is `:disabled="syncStatus === 'syncing' || syncStatus === 'offline'"`, and calls `syncService.syncNow()` on click; apply `disabled` visual style (opacity/cursor)
- [x] T012 [US4] Add `<SyncNowButton>` to the nav in `frontend/src/App.vue`: import `SyncNowButton.vue`, place it immediately after `<SyncStatusIcon>` in the nav template, and add minimal nav styles so it fits the existing nav bar layout

**Checkpoint**: Sync Now button visible in nav on all pages, all 4 state contract tests pass (T010).

---

## Phase 7: Polish & Cross-Cutting Concerns

- [x] T013 [P] Update `frontend/src/components/tests/SyncStatusIcon.spec.ts` to add `syncNow: vi.fn()` to the `syncService` mock object (prevents test breakage after `sync.ts` now exports `syncNow`)
- [x] T014 [P] Update `frontend/src/pages/tests/ContactForm.spec.ts` sync mock to include `syncNow: vi.fn()` for the same reason
- [x] T015 Run the full frontend test suite (`npm run test` in `frontend/`) and confirm all tests pass with no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — blocks US4 only
- **US1 (Phase 3)**: Depends on Phase 1 only — independent of US2, US3, US4
- **US2 (Phase 4)**: Depends on Phase 1 only — independent, can run in parallel with US1
- **US3 (Phase 5)**: Depends on Phase 1 only — independent, can run in parallel with US1/US2
- **US4 (Phase 6)**: Depends on Phase 2 (needs `syncNow()`) — independent of US1/US2/US3
- **Polish (Phase 7)**: Depends on all phases above being complete

### User Story Dependencies

- **US1 (P1)**: Can start after T001 — no story dependencies
- **US2 (P2)**: Can start after T001 — no story dependencies
- **US3 (P3)**: Can start after T001 — no story dependencies
- **US4 (P2)**: Requires T002 (syncNow exposed) — no dependency on US1/US2/US3

### Within Each User Story

- Tests MUST be written and FAIL before implementation begins (constitution V)
- `liveQuery` subscription before removing old one-shot reads
- Unsubscribe cleanup before removing loading flags

### Parallel Opportunities

- After T001: T003 (US1 test), T006 (US2 test), T008 (US3 test), T010 (US4 test) can all be written in parallel — they are in different files
- T007 (US2 impl) and T009 (US3 impl) can run in parallel — different files
- T013 and T014 (polish mocks) can run in parallel — different files

---

## Parallel Example: Writing All Tests First

```bash
# After T001 and T002 are done, write all four test files in parallel:
T003: frontend/src/pages/tests/ContactList.spec.ts       # US1 liveQuery test
T006: frontend/src/pages/tests/ContactDetail.spec.ts     # US2 liveQuery test (new)
T008: frontend/src/components/tests/InteractionFeed.spec.ts  # US3 liveQuery test (new)
T010: frontend/src/components/tests/SyncNowButton.spec.ts    # US4 button state tests (new)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001 — Confirm liveQuery available
2. T002 — Expose syncNow (quick, needed later)
3. T003 — Write failing test
4. T004 — Migrate contacts store
5. T005 — Fix existing test mock
6. **STOP AND VALIDATE**: contact list updates without page reload ✅

### Incremental Delivery

1. T001–T005 → Contact list reactive (MVP, most-used view)
2. T006–T007 → Contact detail reactive
3. T008–T009 → Interaction feed reactive
4. T010–T012 → Sync Now button in nav
5. T013–T015 → Polish and full test pass

---

## Notes

- `liveQuery` returns a Dexie `Observable` (not RxJS). It has `.subscribe({ next, error })` and returns `{ unsubscribe }`.
- In Pinia stores (no component lifecycle), subscriptions live for the store's lifetime — no `onUnmounted` needed.
- In page components (`ContactDetailPage`), always call `sub.unsubscribe()` in `onUnmounted` to avoid memory leaks.
- The contacts store's `loadContacts()` must remain callable (pages call it on mount) — make it a no-op or return `contacts.value` directly to avoid breaking callers.
- Commit after each user story phase (after T005, T007, T009, T012, T015).
