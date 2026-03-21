# Research: Personal CRM Web Application

**Phase**: 0 — Research
**Branch**: `001-personal-crm`
**Date**: 2026-03-20

---

## 1. Offline-First Storage & Sync

### Decision
**Dexie.js** (IndexedDB wrapper) for local storage + **timestamp-based delta sync with an outbox queue** for backend sync.

### Rationale
- Single user → no conflict resolution needed; last-write-wins is always correct.
- IndexedDB is the only viable offline storage for relational CRM data in a browser (localStorage is synchronous, 5 MB capped, untyped).
- Dexie.js replaces ~400 lines of raw IndexedDB boilerplate, provides TypeScript-typed schemas and versioned migrations, and weighs ~23 KB minified. It earns its dependency slot.
- Delta sync (pull `?since=<timestamp>`, then push outbox batch) is the simplest correct pattern for a single user: no CRDTs, no event sourcing infrastructure, no full-payload round trips.

### Outbox pattern
Every write lands in IndexedDB first (optimistic), then adds an entry to a local `outbox` Dexie table. A `SyncService` runs on app mount, on `navigator.onLine` becoming true, and on a 30-second interval when online. Sync cycle: pull server deltas → upsert locally → push unsynced outbox entries → mark as synced.

### Soft-delete tension with spec
The spec requires hard delete (FR-012). Delta sync requires tombstones — if a record is hard-deleted server-side, the pulling client never learns to remove it. **Resolution**: server uses a `deleted_at` / `is_deleted` soft-delete flag as an internal sync mechanism. The record is invisible to all non-sync queries (not exposed via any list/detail endpoint). A scheduled task permanently hard-deletes tombstones older than 30 days. From the user's perspective, the contact is gone immediately. This is documented in the Complexity Tracking table in plan.md.

### Alternatives considered
| Alternative | Rejected because |
|---|---|
| localStorage | 5 MB cap, synchronous, no structured queries |
| Raw IndexedDB | Verbose callback API, error-prone transaction management |
| PouchDB | Designed for CouchDB replication — incompatible with Django REST backend |
| RxDB | Significant bundle size, paid features, violates dependency-minimisation |
| CRDT (Yjs/Automerge) | Multi-user collaboration primitives; zero benefit for single-user app |
| Full database replication (ElectricSQL, PowerSync) | Require PostgreSQL; constitution mandates SQLite |
| Service Worker + Background Sync API | Limited browser support; adds SW lifecycle complexity; foreground outbox covers 100% of use case |

### State management
**Pinia** stores hold reactive UI state. Composables read from Dexie and write to both Dexie and the Pinia store atomically. UI never calls the Django API directly — only `SyncService` does.

### Key implementation notes
- Client-generated UUIDs (`crypto.randomUUID()`) as primary keys — offline-created records need a stable ID before server confirmation.
- Store `last_sync_at` epoch ms in `localStorage` (single scalar, not a DB row).
- Auth boundary: on 401 during sync, redirect to login without discarding the outbox.
- GPS coordinates captured at write time on the client, included in the outbox payload; server stores as-is (no server-side geolocation).

---

## 2. Map Library

### Decision
**Leaflet.js** + **@vue-leaflet/vue-leaflet** + **Leaflet.markercluster**

### Rationale
- Leaflet core is ~42 KB gzipped. MapLibre GL JS is ~250 KB+, OpenLayers ~300 KB+. For a <256 MB RAM VPS, Leaflet is the only responsible choice.
- OpenStreetMap tiles require no API key, no account — consistent with Privacy-First principle (contact GPS coordinates never sent to a third party; only tile grid coordinates are requested from OSM).
- `Leaflet.markercluster` is the de-facto standard plugin for pin clustering with count badges.
- `@vue-leaflet/vue-leaflet` is the only actively maintained Vue 3 wrapper for Leaflet.

### Alternatives considered
| Library | Rejected because |
|---|---|
| MapLibre GL JS | ~250 KB gzipped; WebGL GPU dependency; no maintained Vue 3 wrapper |
| OpenLayers | ~300 KB; verbose API; no Vue 3 wrapper |

### Key integration notes
- Vite breaks Leaflet's default marker icon paths — fix once globally via `L.Icon.Default.mergeOptions()` in `main.ts`.
- `@vue-leaflet/vue-leaflet` has no cluster component; use raw Leaflet `L.markerClusterGroup()` inside `onMounted` via the map ref's `leafletObject`.
- Install: `npm install @vue-leaflet/vue-leaflet leaflet leaflet.markercluster` + dev types `@types/leaflet @types/leaflet.markercluster`.

---

## 3. Full-Text Search

### Decision
**Django ORM `icontains` with Q objects** — no additional dependency.

### Rationale
At 1,000 contacts, a multi-field `LIKE '%term%'` query on SQLite returns results in <50 ms — well within the 2-second budget of SC-008. The complexity and maintenance overhead of FTS5 shadow tables, django-watson index sync, or client-side caching are unjustifiable at this scale.

### Query pattern
```python
Contact.objects.filter(
    Q(name__icontains=q) |
    Q(organisation__icontains=q) |
    Q(context_tag__icontains=q) |
    Q(phones__number__icontains=q) |
    Q(emails__address__icontains=q) |
    Q(interaction_entries__content__icontains=q)
).distinct().select_related().prefetch_related("phones", "emails", "interaction_entries")[:50]
```

`.distinct()` is required due to JOIN fan-out across related tables. Hard cap at 50 results.

### API contract
`GET /api/contacts/?q=<term>` — 300 ms debounce on the frontend. Reject queries shorter than 2 characters server-side.

### Alternatives considered
| Option | Rejected because |
|---|---|
| SQLite FTS5 | Requires shadow virtual table + triggers; migration complexity; performance gain irrelevant at 1,000 rows |
| django-watson | Extra dependency + `post_save` sync concern; adds no UX value at this scale |
| Client-side Fuse.js | Full corpus must be loaded into browser (unbounded interaction entry text); fuzzy matching poor UX for phone/email lookup |

### Future escape hatch
django-watson can be added with minimal API-contract changes if the dataset grows significantly.

---

## 4. Docker Setup & Toolchain

### Decision: Multi-stage Dockerfile + WhiteNoise + gunicorn

**Dockerfile pattern**: Two-stage build — Node.js stage builds Vue assets, Python stage runs Django. Vue dist is copied into `STATIC_ROOT` at build time; no runtime Node container.

**Static asset serving**: **WhiteNoise** (`whitenoise>=6`) — serves compressed assets from within the gunicorn process. Zero additional RAM, no sidecar. Apache2 on the host handles TLS termination and proxies all traffic to `127.0.0.1:8000`.

**Vite base URL**: must be set to `/static/spa/` to match Django's `STATIC_URL`.

### Python & Django versions
- **Python 3.13** (`python:3.13-slim`, `linux/amd64`)
- **Django 5.2 LTS** (supported until April 2028 — suitable for a long-running personal app with infrequent upgrades)
- **Django-Ninja** latest stable (≥1.3)

### Gunicorn sizing (1 vCPU, <256 MB RAM)
- `--workers 2 --threads 2` (or `--workers 1 --threads 4` for lower RSS)
- `--worker-class sync` (SQLite is synchronous; async workers add no benefit)
- `--timeout 30`

### SQLite production notes
- Enable WAL mode via `post_migrate` signal: `PRAGMA journal_mode=WAL;`
- Mount DB on a Docker volume (`./data:/app/data`) — never inside the container layer
- Daily backup cron on the host

### Testing stack
| Layer | Stack |
|---|---|
| Backend | `pytest` + `pytest-django` + `factory-boy` + `ninja.testing.TestClient` |
| Frontend | `vitest` + `@vue/test-utils` + `@vitest/coverage-v8` |
| E2E | Deferred (overkill for single-user, violates simplicity principle) |

SQLite in-memory for test runs: `TEST: {NAME: ":memory:"}` in `DATABASES`.

### Alternatives considered
| Option | Rejected because |
|---|---|
| Nginx sidecar for static files | Second container; more RAM; more moving parts |
| Apache serving files directly from Docker volume | Tighter coupling between host and container; unnecessary complexity |
| Async gunicorn workers (uvicorn) | No benefit with SQLite; adds async complexity |
| Playwright/Cypress E2E | Overkill for single-user app; violates simplicity principle |

---

## 5. Architecture Summary (All Decisions)

| Concern | Decision |
|---|---|
| Backend language | Python 3.13 |
| Backend framework | Django 5.2 LTS + Django-Ninja ≥1.3 |
| Frontend framework | Vue 3 + TypeScript + Vite |
| Offline storage | Dexie.js (IndexedDB) |
| Sync strategy | Outbox + timestamp delta sync |
| State management | Pinia |
| Map | Leaflet + @vue-leaflet/vue-leaflet + Leaflet.markercluster |
| Search | Django ORM icontains + Q objects |
| Static files | WhiteNoise via gunicorn |
| Containerisation | Multi-stage Docker (Node builder → Python runtime) |
| Reverse proxy | Apache2 on Debian 13 host (TLS termination) |
| Database | SQLite via Django ORM (WAL mode in prod) |
| Auth | Django session framework (username/password) |
| Backend tests | pytest + pytest-django + factory-boy |
| Frontend tests | Vitest + Vue Test Utils |
