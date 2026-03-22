# Implementation Plan: Fix Sync — UI Does Not Reflect Data Changes Without Page Reload

**Branch**: `006-fix-sync-ui-refresh` | **Date**: 2026-03-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-fix-sync-ui-refresh/spec.md`

## Summary

Replace all one-shot `onMounted` IndexedDB reads in data-displaying views with reactive `liveQuery()` subscriptions (Dexie built-in, no new packages). Add a "Sync Now" button to the global nav bar that triggers an immediate sync cycle and is disabled while syncing or offline.

## Technical Context

**Language/Version**: TypeScript 5 / Vue 3
**Primary Dependencies**: `dexie` (already installed — `liveQuery` is a named export, no new package needed), Pinia, Vue Router 4
**Storage**: IndexedDB via Dexie.js (no schema changes)
**Testing**: Vitest + @vue/test-utils
**Target Platform**: Browser (SPA)
**Project Type**: Web application (frontend-only change)
**Performance Goals**: UI updates within 2 seconds of IndexedDB write (SC-001); local writes reflected under 200ms (SC-003)
**Constraints**: No new npm packages; must not break existing optimistic write path; must not disrupt in-progress edits
**Scale/Scope**: 3 views + 2 stores + sync service + nav component

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | ✅ PASS | No changes to data storage, transmission, or access control |
| II. Simplicity Over Features | ✅ PASS | `liveQuery` is the idiomatic Dexie solution; zero new dependencies |
| III. Data Integrity | ✅ PASS | No write-path changes; read subscriptions cannot corrupt data |
| IV. User-Owned Data | ✅ PASS | No changes to export or delete paths |
| V. Test-Driven Development | ✅ REQUIRED | Tests must be written and failing before implementation; see Phase 1 |
| VI. Atomic Commits | ✅ REQUIRED | One commit per logical unit: contacts store, detail page, interactions store, sync button |

**Post-Phase-1 re-check**: No violations introduced.

## Root Cause

All three data-displaying surfaces load data once on mount and store results in a plain `ref`. Dexie writes from the sync cycle are never observed:

| Surface | Current pattern | Problem |
|---------|----------------|---------|
| `ContactListPage.vue` | `onMounted → contactStore.loadContacts()` → `ref<Contact[]>` | Sync writes to `db.contacts` but never calls `loadContacts()` again |
| `ContactDetailPage.vue` | `onMounted → db.contacts.get(id)` + 3 one-off queries | Direct DB reads, no subscription |
| `InteractionFeed.vue` | `onMounted → interactionStore.loadForContact()` → `ref<InteractionEntry[]>` | Same pattern as contacts store |

## Design

### Reactive queries via `liveQuery`

`liveQuery(() => query)` (exported by `dexie`) returns an Observable that re-runs the query function and emits fresh results whenever the queried tables change. Subscribing it to a Vue `ref` makes the UI automatically reactive to any IndexedDB write — whether from a local action or the sync cycle.

Pattern used in all affected files:

```ts
import { liveQuery } from 'dexie'
import { ref, onUnmounted } from 'vue'

const contacts = ref<Contact[]>([])
const sub = liveQuery(() =>
  db.contacts.orderBy('name').toArray()
    .then(all => all.filter(c => !c.is_deleted))
).subscribe({
  next: val => { contacts.value = val },
  error: err => console.error('[liveQuery]', err),
})
onUnmounted(() => sub.unsubscribe())
```

### Contacts store migration

- Replace `contacts = ref<Contact[]>([])` + manual `loadContacts()` call in mutations with a single `liveQuery` subscription initialised at store creation.
- `loadContacts()` kept as a no-op or thin wrapper for call-site compatibility.
- All mutations (`createContact`, `updateContact`, `deleteContact`) no longer need to call `loadContacts()` at the end.

### Interactions store migration

- Replace `entries = ref<InteractionEntry[]>([])` + `loadForContact()` with a `liveQuery` scoped to `currentContactId`.
- When `currentContactId` changes, the live query must re-subscribe with the new ID. Use `watch` on `currentContactId` to unsubscribe the old and subscribe the new query.

### ContactDetailPage migration

- Replace the 4 one-off `db.xxx` reads in `loadContact()` with 4 individual `liveQuery` subscriptions (contact, phones, emails, history), each scoped to `id`.
- The `loading` state is set to `false` after the first emission of each subscription.

### Sync Now button

- Expose `syncCycle()` publicly on `SyncService` as `syncNow()`.
- Add `SyncNowButton.vue` component to the global nav in `App.vue`, placed next to `SyncStatusIcon`.
- Button disabled when `syncStatus.value === 'syncing'` or `syncStatus.value === 'offline'`.
- No new state required — `syncStatus` already exported from `sync.ts` covers all states.

## Project Structure

### Documentation (this feature)

```text
specs/006-fix-sync-ui-refresh/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── contracts/
│   └── sync-now-button.md   # UI contract for Sync Now button states
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (changed files only)

```text
frontend/src/
├── stores/
│   ├── contacts.ts              # Replace ref + loadContacts() with liveQuery
│   └── interactions.ts          # Replace ref + loadForContact() with liveQuery + watch
├── services/
│   └── sync.ts                  # Expose public syncNow() method
├── pages/
│   └── ContactDetailPage.vue    # Replace onMounted reads with liveQuery subscriptions
├── components/
│   └── SyncNowButton.vue        # New — Sync Now button with disabled states
└── App.vue                      # Add SyncNowButton to nav

frontend/src/pages/tests/
├── ContactList.spec.ts          # Add liveQuery reactivity tests
└── ContactForm.spec.ts          # Verify no regression on optimistic writes

frontend/src/components/tests/
└── SyncNowButton.spec.ts        # New — button state tests
```

## Complexity Tracking

No constitution violations. Table omitted.
