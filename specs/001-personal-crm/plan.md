# Implementation Plan: Personal CRM Web Application

**Branch**: `001-personal-crm` | **Date**: 2026-03-20 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-personal-crm/spec.md`

---

## Summary

Build a local-first personal CRM webapp where a single authenticated user can add contacts, log timestamped interaction entries, track GPS location of each write (with a privacy toggle), browse contacts on a map, and search across all fields. Data is stored offline in IndexedDB (Dexie.js) and synced to a Django + SQLite backend via a timestamp-based delta sync outbox pattern. The stack is Python 3.13 + Django 5.2 LTS + Django-Ninja for the API, Vue 3 + TypeScript SPA served via WhiteNoise through gunicorn, containerised as a single Docker image with Apache2 on the host for TLS termination.

---

## Technical Context

**Language/Version**: Python 3.13 (backend) · Node 22 / TypeScript 5 (frontend build)
**Primary Dependencies**: Django 5.2 LTS, Django-Ninja ≥1.3, gunicorn, WhiteNoise ≥6, Dexie.js, Pinia, Vue Router 4, Leaflet.js, @vue-leaflet/vue-leaflet, Leaflet.markercluster
**Storage**: SQLite (Django ORM + WAL mode) · IndexedDB (Dexie.js, frontend offline cache)
**Testing**: pytest + pytest-django + factory-boy (backend) · Vitest + @vue/test-utils (frontend)
**Target Platform**: Single Linux/amd64 VPS (Debian 13 host, Docker container)
**Project Type**: Web application (SPA + REST API)
**Performance Goals**: Search results within 2 s for ≤1,000 contacts (SC-008); contact creation in <60 s from app open (SC-001)
**Constraints**: <256 MB RAM at idle; fully functional offline (SC-006); single user; no external services at runtime (map tiles via OpenStreetMap only)
**Scale/Scope**: 1 user, ≤1,000 contacts, 1 VPS instance

---

## Constitution Check

*Gate evaluation against [constitution.md](../../.specify/memory/constitution.md) v1.3.0*

### I. Privacy-First ✅ PASS

- All contact and GPS data stays on the user's own VPS — no third-party analytics, no cloud sync service.
- OpenStreetMap tile requests contain only geographic tile coordinates, never contact GPS coordinates.
- GPS collection is opt-out via `PrivacySettings.location_tracking_enabled` (FR-009, FR-010).
- Django session auth; no third-party OAuth.

### II. Simplicity Over Features ⚠️ JUSTIFIED (see Complexity Tracking)

- All features in scope are explicitly required by the spec (no speculative additions).
- Three added dependencies (Dexie.js, Leaflet.js, @vue-leaflet/vue-leaflet + markercluster) each have a justified entry in the Complexity Tracking table.
- Offline-first sync is a mandatory requirement (SC-006) — complexity is required, not speculative.
- No E2E tests, no GraphQL, no event sourcing, no CRDT, no managed cloud services.

### III. Data Integrity ✅ PASS

- Outbox pattern: writes go to IndexedDB first, then the sync queue — no silent data loss.
- All write failures surface as visible UI errors.
- Django migrations are the sole schema change mechanism (hand-written SQL prohibited by constitution).
- SQLite WAL mode enabled for production to prevent write contention.
- Soft-delete tombstones (see Complexity Tracking) prevent sync gaps; hard purge after 30 days.

### IV. User-Owned Data ⚠️ TENSION (see Complexity Tracking)

- The spec requires hard delete; sync requires tombstones (soft-delete).
- **Resolution**: tombstones are purged after 30 days by an automated job. The contact is invisible in all user-facing endpoints from the moment of deletion. No data is retained beyond the tombstone grace period. The constitution's intent ("no hidden retention") is met.
- Data export (CSV/JSON) is referenced in Principle IV but deferred per the spec's Assumptions section. Marked as a future requirement.

### V. Test-Driven Development ✅ MANDATORY

- TDD Red-Green-Refactor cycle is non-negotiable.
- All tasks in `tasks.md` must include test tasks that are completed before implementation tasks.
- Integration tests must cover all CRUD paths for Contact, InteractionEntry, ContactHistory, PrivacySettings, and the sync endpoints.

### VI. Atomic Commits ✅ MANDATORY

- Each task = one commit. No bundling unrelated changes.
- Commit messages describe intent, not files changed.

### Stack Constraints Check

| Constraint | Status |
|---|---|
| Backend: Django + Django-Ninja | ✅ Confirmed |
| Frontend: Vue 3 + TypeScript | ✅ Confirmed |
| Auth: Django sessions (username/password) | ✅ Confirmed |
| Storage: SQLite via Django ORM | ✅ Confirmed |
| Deploy: Docker + gunicorn + Apache2 | ✅ Confirmed |
| RAM <256 MB at idle | ✅ Single gunicorn container + WhiteNoise (no sidecar) |
| Image: linux/amd64 | ✅ Dockerfile target set |
| No managed cloud services | ✅ OSM tiles only |

---

## Project Structure

### Documentation (this feature)

```text
specs/001-personal-crm/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── api.md           # Phase 1 output — Django-Ninja API contract
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created here)
```

### Source Code (repository root)

```text
backend/
├── crm/
│   ├── settings/
│   │   ├── base.py
│   │   └── production.py
│   ├── api.py             # NinjaAPI instance; add_router calls
│   └── urls.py
├── contacts/
│   ├── models.py          # Contact, ContactPhone, ContactEmail, InteractionEntry, ContactHistory
│   ├── schemas.py         # ContactIn, ContactOut, InteractionEntryIn, etc.
│   └── router.py          # /contacts/, /contacts/{id}/interactions/, /map/pins/
├── sync/
│   ├── router.py          # /sync/pull/, /sync/push/
│   └── schemas.py
├── users/
│   ├── router.py          # /auth/login, /auth/logout, /auth/me
│   └── schemas.py
├── settings_app/
│   ├── models.py          # PrivacySettings
│   ├── schemas.py
│   └── router.py          # /settings/privacy/
├── conftest.py
├── manage.py
└── requirements.txt

frontend/
├── src/
│   ├── components/        # Reusable UI components
│   ├── pages/             # ContactListPage, ContactDetailPage, MapPage, SettingsPage, LoginPage
│   ├── stores/            # Pinia: useContactStore, useInteractionStore, useSettingsStore
│   ├── services/
│   │   ├── db.ts          # Dexie schema and database instance
│   │   └── sync.ts        # SyncService: pull/push cycle, outbox management
│   └── composables/       # useGeolocation, useSearch
├── tests/
└── vite.config.ts

Dockerfile                 # Multi-stage: Node builder → Python runtime
docker-compose.yml
```

**Structure Decision**: Web application layout (Option 2). Backend and frontend are separate directories in the monorepo. The Vue SPA is built at image build time and served via WhiteNoise from within the Django/gunicorn container — no runtime Node or nginx containers.

---

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| Dexie.js dependency | Offline-first storage (SC-006) requires IndexedDB; Dexie replaces ~400 lines of raw callback-based IndexedDB code and provides typed migrations | Raw IndexedDB is verbose, error-prone, and untyped — introduces more bugs than it saves dependencies |
| Leaflet.js + vue-leaflet + markercluster dependencies | Map view (FR-007b) is a required feature; these are the only free, Vue 3 compatible, lightweight map stack | No free alternative with Vue 3 support at <50 KB; building from scratch is out of scope |
| Soft-delete tombstones (30-day retention) | Delta sync requires the server to communicate deletions to the client; hard-deletes are invisible to a pulling client | Without tombstones, deleted contacts reappear on the client after the next sync; this is a data integrity violation worse than the 30-day retention window |
| IndexedDB outbox queue | Offline write queue is required for SC-006 (offline-first, no data loss); no simpler mechanism exists in browsers | localStorage cannot queue structured relational changes; Service Worker Background Sync has limited/inconsistent browser support |
