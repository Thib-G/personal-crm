# Data Model: Personal CRM Web Application

**Phase**: 1 — Design
**Branch**: `001-personal-crm`
**Date**: 2026-03-20

---

## Overview

The data model is intentionally flat. All records are scoped to a single user (no multi-tenancy). Five core entities cover the full feature set: `Contact`, `ContactPhone`, `ContactEmail`, `InteractionEntry`, `ContactHistory`, and `PrivacySettings`.

---

## Entities

### User *(Django built-in)*

Provided by `django.contrib.auth`. No custom fields required for v1. Authentication is username/password via Django's session framework.

---

### Contact

The central record. All other entities are children of a Contact.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK, client-generated | `crypto.randomUUID()` — set by frontend before sync |
| `owner` | FK → User | NOT NULL, `on_delete=PROTECT` | Single-user app; enforced for future safety |
| `name` | CharField(255) | NOT NULL | Only required field |
| `context_tag` | CharField(20) | NOT NULL, choices: event/work/personal/other | Default: `other` |
| `organisation` | CharField(255) | nullable | |
| `created_at` | DateTimeField | NOT NULL, set at first save | Immutable after creation |
| `updated_at` | DateTimeField | NOT NULL, auto-updated | Sync anchor — used in delta pull |
| `created_lat` | DecimalField(9,6) | nullable | GPS at creation time |
| `created_lng` | DecimalField(9,6) | nullable | GPS at creation time |
| `is_deleted` | BooleanField | NOT NULL, default False | Tombstone flag for sync |
| `deleted_at` | DateTimeField | nullable | Set on soft-delete; permanent hard-delete after 30 days |

**Indexes**: `name` (for ordering), `updated_at` (for delta sync pull), `is_deleted` (to filter tombstones from all non-sync queries).

**Validation rules**:
- `name` must not be blank.
- `context_tag` must be one of: `event`, `work`, `personal`, `other`.

**State transitions**:
```
active → soft-deleted (user confirms delete)
soft-deleted → hard-deleted (automated purge after 30 days)
```

---

### ContactPhone

One-to-many: a Contact may have multiple phone numbers.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK, client-generated | |
| `contact` | FK → Contact | NOT NULL, `on_delete=CASCADE` | Cascade hard-delete when Contact is purged |
| `number` | CharField(50) | NOT NULL | No format validation in v1 |
| `updated_at` | DateTimeField | NOT NULL, auto-updated | |

---

### ContactEmail

One-to-many: a Contact may have multiple email addresses.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK, client-generated | |
| `contact` | FK → Contact | NOT NULL, `on_delete=CASCADE` | |
| `address` | CharField(254) | NOT NULL | Standard email max length |
| `updated_at` | DateTimeField | NOT NULL, auto-updated | |

---

### InteractionEntry

An immutable timestamped note per interaction. Append-only: once saved, entries cannot be edited.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK, client-generated | |
| `contact` | FK → Contact | NOT NULL, `on_delete=CASCADE` | |
| `content` | TextField | NOT NULL | Free-text; minimum 1 character |
| `created_at` | DateTimeField | NOT NULL, set at first save | Immutable |
| `updated_at` | DateTimeField | NOT NULL, auto-updated | Sync anchor |
| `lat` | DecimalField(9,6) | nullable | GPS at creation time |
| `lng` | DecimalField(9,6) | nullable | GPS at creation time |

**Validation rules**:
- `content` must not be blank (acceptance scenario 4 of User Story 4).

**Ordering**: newest-first (`-created_at`) when displayed as a feed.

---

### ContactHistory

Append-only audit log of Contact field changes. One entry per changed field per save operation. Never edited or deleted except via cascade when the Contact is hard-deleted.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | Server-generated (history is server-side only, not synced from client) |
| `contact` | FK → Contact | NOT NULL, `on_delete=CASCADE` | |
| `field_name` | CharField(100) | NOT NULL | E.g. `"name"`, `"organisation"`, `"context_tag"` |
| `old_value` | TextField | nullable | `None` on first creation |
| `new_value` | TextField | NOT NULL | |
| `changed_at` | DateTimeField | NOT NULL, auto-set | |
| `lat` | DecimalField(9,6) | nullable | GPS at change time (from client payload) |
| `lng` | DecimalField(9,6) | nullable | GPS at change time |

**Notes**:
- History entries are generated server-side by the update endpoint by comparing old and new field values. The frontend does not send `ContactHistory` objects.
- Phone/email changes (add, remove) are captured as history entries with `field_name = "phones"` or `"emails"` and serialised old/new values.

---

### PrivacySettings

One per user. Created with defaults on first login.

| Field | Type | Constraints | Notes |
|---|---|---|---|
| `id` | UUID | PK | |
| `user` | OneToOneField → User | NOT NULL, `on_delete=CASCADE` | |
| `location_tracking_enabled` | BooleanField | NOT NULL, default True | Master toggle for GPS collection |
| `updated_at` | DateTimeField | NOT NULL, auto-updated | |

**Behaviour**:
- When `location_tracking_enabled = False`, the frontend does not request or send GPS coordinates, regardless of OS-level permission state.
- When the OS denies location permission, the frontend treats it as if tracking is disabled for that write (no error shown on save; a one-time informational notice is shown per session).

---

## Relationships Diagram

```
User
 └── PrivacySettings (1:1)
 └── Contact (1:many)
      ├── ContactPhone (1:many)
      ├── ContactEmail (1:many)
      ├── InteractionEntry (1:many)
      └── ContactHistory (1:many, append-only)
```

---

## Dexie (IndexedDB) Schema

The frontend mirrors the server schema in IndexedDB. The `outbox` table is frontend-only.

```typescript
// db.ts — Dexie schema (version 1)
db.version(1).stores({
  contacts:           '&id, name, context_tag, updated_at, is_deleted',
  contact_phones:     '&id, contact_id, updated_at',
  contact_emails:     '&id, contact_id, updated_at',
  interaction_entries:'&id, contact_id, created_at, updated_at',
  contact_history:    '&id, contact_id, changed_at',  // pulled from server only
  privacy_settings:   '&id',
  outbox:             '++_seq, entity, operation, synced, created_at',
})
```

- `&id` = unique primary key (UUID string).
- `++_seq` = auto-increment integer for outbox ordering.
- Indexed fields support efficient filtering in composables.

---

## Django Migration Notes

- All models use `UUIDField(primary_key=True)` — no auto-increment integer PKs.
- The `owner` FK is added from day one even though v1 is single-user.
- `deleted_at` / `is_deleted` are added in the initial migration; all non-sync querysets must include `.filter(is_deleted=False)`.
- A custom manager `ActiveContactManager` with `.filter(is_deleted=False)` is the default manager; a `AllObjectsManager` (unfiltered) is available for sync endpoints.
- Schema changes require a new Django migration file; hand-written SQL is prohibited.
