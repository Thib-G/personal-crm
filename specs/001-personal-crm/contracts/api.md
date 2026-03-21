# API Contract: Personal CRM

**Version**: 1.0
**Backend**: Django 5.2 LTS + Django-Ninja ≥1.3
**Base URL**: `/api/`
**Auth**: Django session (cookie-based). All endpoints except `/api/auth/login/` require an authenticated session. Unauthenticated requests return `401 Unauthorized`.
**Content-Type**: `application/json`

---

## Auth

### `POST /api/auth/login/`

Login with username and password. Sets a session cookie on success.

**Request**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response `200 OK`**
```json
{
  "id": "integer",
  "username": "string"
}
```

**Errors**
- `400` — missing fields
- `401` — invalid credentials

---

### `POST /api/auth/logout/`

Destroys the current session.

**Response `204 No Content`**

---

### `GET /api/auth/me/`

Returns the currently authenticated user.

**Response `200 OK`**
```json
{
  "id": "integer",
  "username": "string"
}
```

---

## Contacts

All contact responses omit `is_deleted=True` records. The sync endpoints are the only place tombstones are visible.

### `GET /api/contacts/`

List all contacts (default: alphabetical by name). Supports search.

**Query parameters**
| Param | Type | Description |
|---|---|---|
| `q` | string (≥2 chars) | Full-text search across name, organisation, context_tag, phones, emails, interaction entry text |
| `ordering` | string | `name` (default), `-name`, `created_at`, `-created_at` |

**Response `200 OK`**
```json
[
  {
    "id": "uuid",
    "name": "string",
    "context_tag": "event|work|personal|other",
    "organisation": "string|null",
    "created_at": "ISO8601",
    "updated_at": "ISO8601",
    "created_lat": "decimal|null",
    "created_lng": "decimal|null",
    "phones": [{ "id": "uuid", "number": "string" }],
    "emails": [{ "id": "uuid", "address": "string" }]
  }
]
```

---

### `POST /api/contacts/`

Create a new contact.

**Request**
```json
{
  "id": "uuid",
  "name": "string",
  "context_tag": "event|work|personal|other",
  "organisation": "string|null",
  "created_at": "ISO8601",
  "created_lat": "decimal|null",
  "created_lng": "decimal|null",
  "phones": [{ "id": "uuid", "number": "string" }],
  "emails": [{ "id": "uuid", "address": "string" }]
}
```

- `id` is client-generated (UUID v4).
- `name` is required and must not be blank.
- All other fields are optional.

**Response `201 Created`** — full contact object (same as GET item, see below).

**Errors**
- `400` — validation failure (blank name, invalid context_tag)
- `409` — contact with this `id` already exists

---

### `GET /api/contacts/{id}/`

Retrieve a single contact with full detail.

**Response `200 OK`**
```json
{
  "id": "uuid",
  "name": "string",
  "context_tag": "event|work|personal|other",
  "organisation": "string|null",
  "created_at": "ISO8601",
  "updated_at": "ISO8601",
  "created_lat": "decimal|null",
  "created_lng": "decimal|null",
  "phones": [{ "id": "uuid", "number": "string" }],
  "emails": [{ "id": "uuid", "address": "string" }],
  "interaction_entries": [
    {
      "id": "uuid",
      "content": "string",
      "created_at": "ISO8601",
      "lat": "decimal|null",
      "lng": "decimal|null"
    }
  ],
  "history": [
    {
      "id": "uuid",
      "field_name": "string",
      "old_value": "string|null",
      "new_value": "string",
      "changed_at": "ISO8601",
      "lat": "decimal|null",
      "lng": "decimal|null"
    }
  ]
}
```

**Errors**
- `404` — not found or belongs to another user

---

### `PATCH /api/contacts/{id}/`

Update a contact's fields. Only send changed fields. Server automatically creates `ContactHistory` entries for each changed field.

**Request**
```json
{
  "name": "string",
  "context_tag": "event|work|personal|other",
  "organisation": "string|null",
  "phones": [{ "id": "uuid", "number": "string" }],
  "emails": [{ "id": "uuid", "address": "string" }],
  "edit_lat": "decimal|null",
  "edit_lng": "decimal|null"
}
```

- `edit_lat` / `edit_lng` are the GPS coordinates at edit time (stored in the `ContactHistory` entries created by this call).
- To remove a phone/email, omit it from the array.
- To add a phone/email, include it with a client-generated UUID.

**Response `200 OK`** — full contact object (same as GET detail).

**Errors**
- `400` — validation failure
- `404` — not found

---

### `DELETE /api/contacts/{id}/`

Soft-delete a contact (sets `is_deleted=True`, `deleted_at=now()`). The contact immediately disappears from all list/detail endpoints. Hard-delete is handled by an automated background job after 30 days.

**Response `204 No Content`**

**Errors**
- `404` — not found

---

## Interaction Entries

### `POST /api/contacts/{contact_id}/interactions/`

Add a new interaction entry to a contact.

**Request**
```json
{
  "id": "uuid",
  "content": "string",
  "created_at": "ISO8601",
  "lat": "decimal|null",
  "lng": "decimal|null"
}
```

- `id` is client-generated.
- `content` is required and must not be blank.

**Response `201 Created`**
```json
{
  "id": "uuid",
  "contact_id": "uuid",
  "content": "string",
  "created_at": "ISO8601",
  "lat": "decimal|null",
  "lng": "decimal|null"
}
```

**Errors**
- `400` — blank content
- `404` — contact not found

---

### `GET /api/contacts/{contact_id}/interactions/`

List all interaction entries for a contact (newest first).

**Response `200 OK`** — array of interaction entry objects (same schema as POST response).

---

## Map Data

### `GET /api/map/pins/`

Returns all GPS-pinned records for the map view: contacts (created location) and interaction entries (entry location). Only records with non-null coordinates are returned.

**Response `200 OK`**
```json
[
  {
    "type": "contact|interaction",
    "id": "uuid",
    "contact_id": "uuid",
    "contact_name": "string",
    "lat": "decimal",
    "lng": "decimal",
    "label": "string",
    "timestamp": "ISO8601"
  }
]
```

- `label` is the contact name for contact pins; the truncated interaction content for interaction pins.

---

## Privacy Settings

### `GET /api/settings/privacy/`

**Response `200 OK`**
```json
{
  "location_tracking_enabled": true
}
```

---

### `PATCH /api/settings/privacy/`

**Request**
```json
{
  "location_tracking_enabled": false
}
```

**Response `200 OK`** — updated settings object.

---

## Sync

These endpoints are called exclusively by the frontend `SyncService`. Not intended for direct user interaction.

### `GET /api/sync/pull/`

Pull all records modified after the given timestamp.

**Query parameters**
| Param | Type | Required | Description |
|---|---|---|---|
| `since` | ISO8601 datetime | Yes | Return all records with `updated_at > since` |

**Response `200 OK`**
```json
{
  "contacts": [...],
  "contact_phones": [...],
  "contact_emails": [...],
  "interaction_entries": [...],
  "contact_history": [...],
  "server_time": "ISO8601",
  "tombstones": [
    { "entity": "contact|interaction_entry", "id": "uuid", "deleted_at": "ISO8601" }
  ]
}
```

- `server_time` is the authoritative timestamp for the client to store as its new `last_sync_at`.
- `tombstones` lists soft-deleted records the client should remove from IndexedDB.
- Contact responses in sync include soft-deleted records (via `AllObjectsManager`).

---

### `POST /api/sync/push/`

Push local outbox changes to the server. Processed as a batch; server applies each operation in order.

**Request**
```json
{
  "changes": [
    {
      "entity": "contact|contact_phone|contact_email|interaction_entry",
      "operation": "create|update|delete",
      "payload": { "...entity fields..." }
    }
  ]
}
```

**Response `200 OK`**
```json
{
  "applied": [
    { "entity": "...", "id": "uuid", "updated_at": "ISO8601" }
  ],
  "errors": [
    { "entity": "...", "id": "uuid", "error": "string" }
  ]
}
```

- Partial success is allowed: errors in the `errors` array do not prevent other changes from being applied.
- Client marks outbox entries as `synced=true` for each `id` in `applied`.

---

## Error Format

All error responses use Django-Ninja's default format:

```json
{
  "detail": "string or list of validation errors"
}
```

Validation errors (400):
```json
{
  "detail": [
    { "loc": ["body", "name"], "msg": "field required", "type": "value_error.missing" }
  ]
}
```
