# Tasks: Personal CRM Web Application

**Input**: Design documents from `/specs/001-personal-crm/`
**Prerequisites**: plan.md ✅ · spec.md ✅ · research.md ✅ · data-model.md ✅ · contracts/api.md ✅ · quickstart.md ✅

**Tests**: TDD is **MANDATORY** per Constitution Principle V. Test tasks appear before implementation tasks in every user story phase. Tests MUST fail before implementation begins.

**Organization**: Tasks are grouped by user story. Each phase ends with an independently testable checkpoint.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel with other [P] tasks in the same phase (different files, no shared dependencies)
- **[Story]**: User story this task belongs to (US1–US6)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the project skeleton. No logic, no models — just directories, configuration files, and tooling.

- [x] T001 Create directory structure: `backend/`, `frontend/`, `specs/` per plan.md project layout
- [x] T002 Initialize Django 5.2 LTS project inside `backend/` (`django-admin startproject crm .`) and create apps: `contacts`, `users`, `sync`, `settings_app`
- [x] T003 [P] Create `backend/requirements.txt` with pinned versions: Django 5.2, django-ninja≥1.3, gunicorn, whitenoise≥6, pytest, pytest-django, factory-boy
- [x] T004 [P] Scaffold Vue 3 + TypeScript Vite project inside `frontend/` (`npm create vue@latest`); add dependencies: pinia, vue-router@4, dexie, @vue-leaflet/vue-leaflet, leaflet, leaflet.markercluster, @types/leaflet, @types/leaflet.markercluster, vitest, @vue/test-utils, @vitest/coverage-v8
- [x] T005 [P] Create Django settings split: `backend/crm/settings/__init__.py`, `backend/crm/settings/base.py` (DEBUG, INSTALLED_APPS, DATABASES pointing to `../data/db.sqlite3`, STATIC_URL/STATIC_ROOT, WhiteNoise middleware), `backend/crm/settings/production.py` (inherits base, DEBUG=False, SECURE_PROXY_SSL_HEADER, CSRF_TRUSTED_ORIGINS)
- [x] T006 [P] Configure pytest-django: `backend/pytest.ini` (DJANGO_SETTINGS_MODULE=crm.settings.base, testpaths=.) and `backend/conftest.py` (shared fixtures: `db`, authenticated API client via `ninja.testing.TestClient`)
- [x] T007 [P] Configure Vitest: `frontend/vitest.config.ts` (environment: jsdom, coverage via v8) and `frontend/src/test/setup.ts` (global test setup)
- [x] T008 [P] Configure Vite: `frontend/vite.config.ts` with `base: '/static/spa/'` for production and `/api/` proxy to `http://localhost:8000` for development
- [x] T009 Create multi-stage `Dockerfile` (Stage 1: `node:22-alpine` runs `npm ci && npm run build`; Stage 2: `python:3.13-slim` installs deps, copies Vue dist to `staticfiles/spa/`, runs `collectstatic`, starts gunicorn with `--workers 2 --threads 2`)
- [x] T010 [P] Create `docker-compose.yml`: single `app` service, port `127.0.0.1:8000:8000`, volume `./data:/app/data`, env `DJANGO_SETTINGS_MODULE=crm.settings.production`
- [x] T011 [P] Create `backend/.env.example` with all required environment variables (SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_PATH) and `.gitignore` entry for `.env`

**Checkpoint**: `docker compose up --build` starts the app on port 8000. No models, no routes — just a working Django 404 page and a Vue blank shell.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Authentication, offline storage schema, sync scaffold, and privacy defaults. Nothing in any user story can be implemented until this phase is complete.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Tests (write FIRST — must FAIL before implementation)

- [x] T012 [P] Write contract tests for `POST /api/auth/login/`, `POST /api/auth/logout/`, `GET /api/auth/me/` in `backend/users/tests/test_auth_contract.py` using `ninja.testing.TestClient`; assert 401 on all data endpoints without a session
- [x] T013 [P] Write integration test: unauthenticated GET /api/contacts/ returns 401; authenticated GET /api/contacts/ returns 200 in `backend/users/tests/test_auth_integration.py`

### Backend implementation

- [x] T014 Create Django-Ninja API assembly: `backend/crm/api.py` (NinjaAPI instance with `auth=django_auth`) and `backend/crm/urls.py` (`path("api/", api.urls)`)
- [x] T015 [P] Implement auth schemas in `backend/users/schemas.py` (LoginIn: username+password; UserOut: id+username)
- [x] T016 [P] Implement auth router in `backend/users/router.py`: `POST /login/` (authenticate + `login()`), `POST /logout/` (`logout()`), `GET /me/` (return current user); add to `backend/crm/api.py`
- [x] T017 [P] Create `PrivacySettings` model in `backend/settings_app/models.py` (UUIDField PK, OneToOne User, location_tracking_enabled BooleanField default True, updated_at auto); generate initial migration; add `post_save` signal on User to auto-create PrivacySettings with defaults
- [x] T018 [P] Create `backend/settings_app/tests/test_privacy_settings.py`: test PrivacySettings is auto-created on new user creation with location_tracking_enabled=True

### Frontend implementation

- [x] T019 Initialize Dexie v1 schema in `frontend/src/services/db.ts`: tables `contacts`, `contact_phones`, `contact_emails`, `interaction_entries`, `contact_history`, `privacy_settings`, `outbox` with indexes per data-model.md
- [x] T020 [P] Create Pinia auth store in `frontend/src/stores/auth.ts`: state (user: null | {id, username}), actions: `checkSession()` (GET /api/auth/me/), `login(username, password)`, `logout()`
- [x] T021 [P] Create settingsStore in `frontend/src/stores/settings.ts`: state (locationTrackingEnabled: boolean, default true), action `load()` (fetches GET /api/settings/privacy/ — returns default true if 404 until US5 adds the endpoint)
- [x] T022 [P] Create `useGeolocation` composable in `frontend/src/composables/useGeolocation.ts`: calls `navigator.geolocation.getCurrentPosition()` only if `settingsStore.locationTrackingEnabled` is true and browser grants permission; returns `{lat, lng}` or `null`; emits one-time toast if OS permission denied while setting is enabled
- [x] T023 Create Vue Router in `frontend/src/router/index.ts`: routes for `/login`, `/contacts`, `/contacts/:id`, `/contacts/:id/edit`, `/contacts/new`, `/map`, `/settings`; navigation guard redirects unauthenticated users to `/login` (checks authStore.user)
- [x] T024 Create `frontend/src/pages/LoginPage.vue`: username/password form, calls `authStore.login()`, redirects to `/contacts` on success, shows error on 401
- [x] T025 Create `frontend/src/App.vue`: `<router-view />` + top navigation bar (Contacts, Map, Settings links); hides nav when on `/login`
- [x] T026 Create SyncService scaffold in `frontend/src/services/sync.ts`: `startSync()` initializes a 30-second interval timer and `navigator.onLine` event listener; `syncCycle()` is a stub that logs "sync cycle" until wired in the Sync phase; `addToOutbox(entry)` writes an OutboxEntry to the Dexie outbox table

**Checkpoint**: `docker compose up` → open app → redirect to `/login` → log in → redirect to `/contacts` (empty list). Logging out redirects back to `/login`. PrivacySettings row auto-created in DB on user creation.

---

## Phase 3: User Story 1 — Add a New Contact (Priority: P1) 🎯 MVP

**Goal**: A user can create a contact with name, optional details, context tag, and GPS location (if permitted). Contact is saved to IndexedDB immediately and queued for sync.

**Independent Test**: Create a contact → verify it appears in the Dexie `contacts` table → verify an outbox entry exists → run `pytest backend/contacts/tests/` → all pass.

### Tests (write FIRST — must FAIL before implementation)

- [x] T027 [P] [US1] Write contract test for `POST /api/contacts/` in `backend/contacts/tests/test_contacts_contract.py`: assert 201 with valid payload (UUID id, name, context_tag), 400 for blank name, 400 for invalid context_tag, 409 for duplicate UUID, 401 without session
- [x] T028 [P] [US1] Write contract test for `GET /api/contacts/{id}/` in `backend/contacts/tests/test_contacts_contract.py`: assert 200 with correct fields, 404 for unknown id
- [x] T029 [P] [US1] Write integration test in `backend/contacts/tests/test_add_contact.py`: POST creates contact with GPS coords; POST with location_tracking_enabled=False stores null GPS; POST with blank name returns 400; PrivacySettings.location_tracking_enabled=False is respected server-side
- [x] T030 [P] [US1] Write unit test for `ContactForm.vue` in `frontend/src/pages/tests/ContactForm.spec.ts`: submit with name filled → calls contactStore.createContact; submit with empty name → shows validation error; GPS coords included in payload when geolocation returns value

### Backend implementation

- [x] T031 [US1] Create `Contact`, `ContactPhone`, `ContactEmail` models in `backend/contacts/models.py` per data-model.md (UUIDField PKs, owner FK, name, context_tag choices, organisation, created_at, updated_at, created_lat/lng, is_deleted, deleted_at); add `ActiveContactManager` (filters is_deleted=False) as default manager; generate migration
- [x] T032 [US1] Create Contact schemas in `backend/contacts/schemas.py`: `ContactPhoneIn`, `ContactEmailIn`, `ContactIn` (id UUID, name, context_tag, organisation nullable, created_at, created_lat/lng nullable, phones list, emails list), `ContactOut` (full response including phones, emails)
- [x] T033 [US1] Implement `POST /api/contacts/` and `GET /api/contacts/{id}/` in `backend/contacts/router.py`; add router to `backend/crm/api.py` under `/contacts/`
- [x] T034 [US1] Add factory classes for Contact, ContactPhone, ContactEmail in `backend/contacts/tests/factories.py` using factory-boy

### Frontend implementation

- [x] T035 [US1] Create contactStore in `frontend/src/stores/contacts.ts`: state (contacts: Contact[]), actions `createContact(payload)` → writes to Dexie `contacts` table + `contact_phones` + `contact_emails`, then calls `syncService.addToOutbox({entity:'contact', operation:'create', payload})`; `loadContacts()` → reads all non-deleted contacts from Dexie
- [x] T036 [US1] Create `frontend/src/pages/AddContactPage.vue`: form with fields (name*, context_tag select, organisation, phone inputs, email inputs, interaction note); on submit calls `useGeolocation()` then `contactStore.createContact()`; shows validation error if name empty; navigates to `/contacts` on success
- [x] T037 [US1] Add "Add Contact" button/route entry to navigation in `frontend/src/App.vue`

**Checkpoint**: Run `pytest backend/contacts/tests/` → all pass. Add a contact in the UI → appears in Dexie → outbox entry created. GPS recorded if permission granted.

---

## Phase 4: User Story 2 — View and Browse Contacts (Priority: P2)

**Goal**: The user can see all contacts in a list, search by any field, and open a contact's detail view.

**Independent Test**: Seed 5 contacts (3 via DB factory, 2 via UI) → search "jo" → only matching contacts shown → open one → all fields and creation location visible.

### Tests (write FIRST — must FAIL before implementation)

- [x] T038 [P] [US2] Write contract test for `GET /api/contacts/` in `backend/contacts/tests/test_contacts_list_contract.py`: assert 200 returns list; `?q=john` returns only matches; `?q=` (1 char) returns 400; unauthenticated returns 401
- [x] T039 [P] [US2] Write integration test in `backend/contacts/tests/test_search.py`: search across name, org, phone, email, context_tag; search with 1 char returns 400; empty result set returns []
- [x] T040 [P] [US2] Write unit test for `ContactListPage.vue` in `frontend/src/pages/tests/ContactList.spec.ts`: renders contacts from store; typing in search field debounces and filters; clicking contact navigates to detail

### Backend implementation

- [x] T041 [US2] Implement `GET /api/contacts/` in `backend/contacts/router.py`: list all active contacts (sorted by name); add `?q` search parameter using Django Q icontains across name, organisation, context_tag, phones__number, emails__address, interaction_entries__content with `.distinct()[:50]`; reject `q` shorter than 2 chars with 400
- [x] T042 [US2] Add `db_index=True` to `Contact.name` and `Contact.organisation` in `backend/contacts/models.py`; generate migration

### Frontend implementation

- [x] T043 [US2] Create `frontend/src/pages/ContactListPage.vue`: renders contacts from `contactStore.contacts` sorted alphabetically; includes search `<input>` with 300 ms debounce that calls `GET /api/contacts/?q=`; each row shows name, context_tag badge, created_at; clicking navigates to `/contacts/:id`
- [x] T044 [US2] Create `frontend/src/pages/ContactDetailPage.vue`: fetches contact from Dexie by id (falls back to API); displays all fields: name, context_tag, org, phones, emails, created_at, GPS (if available); shows empty states for history and interaction feed (filled in US3/US4); includes Edit and Delete buttons (wired in US3)

**Checkpoint**: Run `pytest backend/contacts/tests/` → all pass. Contact list shows all contacts. Search returns matching results. Detail page shows all fields.

---

## Phase 5: User Story 3 — Edit a Contact and View History (Priority: P3)

**Goal**: The user can edit any contact field. Each edit creates an immutable history entry recording changed field, old/new values, timestamp, and GPS.

**Independent Test**: Edit contact name → history entry created in DB with correct old/new values, timestamp, and GPS → GET /api/contacts/{id}/ returns history array → edit history visible in detail view.

### Tests (write FIRST — must FAIL before implementation)

- [x] T045 [P] [US3] Write contract test for `PATCH /api/contacts/{id}/` in `backend/contacts/tests/test_contacts_edit_contract.py`: assert 200 with updated fields; assert ContactHistory entries created for each changed field; GPS coords in history when provided; 400 for blank name; 404 for unknown id
- [x] T046 [P] [US3] Write contract test for `DELETE /api/contacts/{id}/` in `backend/contacts/tests/test_contacts_delete_contract.py`: assert 204; subsequent GET /api/contacts/{id}/ returns 404; contact not in GET /api/contacts/ list
- [x] T047 [P] [US3] Write integration test in `backend/contacts/tests/test_edit_history.py`: edit name → history created with old+new value; edit phone → history captures previous phone list; delete contact → soft-deleted (is_deleted=True, deleted_at set); history lost after hard delete

### Backend implementation

- [x] T048 [US3] Create `ContactHistory` model in `backend/contacts/models.py` (UUID PK server-generated, contact FK, field_name, old_value nullable, new_value, changed_at auto, lat/lng nullable); generate migration
- [x] T049 [US3] Add `ContactHistoryOut` schema to `backend/contacts/schemas.py`; update `ContactOut` to include `history: list[ContactHistoryOut]`
- [x] T050 [US3] Implement `PATCH /api/contacts/{id}/` in `backend/contacts/router.py`: accept `ContactPatchIn` (all fields optional + `edit_lat`/`edit_lng`); diff old vs new values and create one `ContactHistory` entry per changed field; update `updated_at`
- [x] T051 [US3] Implement `DELETE /api/contacts/{id}/` in `backend/contacts/router.py`: set `is_deleted=True` and `deleted_at=now()` (soft-delete); return 204
- [x] T052 [US3] Add `ContactPatchIn` schema (all optional fields) to `backend/contacts/schemas.py`
- [x] T053 [US3] Add factory class for `ContactHistory` in `backend/contacts/tests/factories.py`

### Frontend implementation

- [x] T054 [US3] Update contactStore in `frontend/src/stores/contacts.ts`: add `updateContact(id, patch)` action → updates Dexie contact + phones + emails, adds outbox entry `{entity:'contact', operation:'update', payload: {...patch, edit_lat, edit_lng}}`; add `deleteContact(id)` action → marks Dexie contact `is_deleted=true`, adds outbox entry `{operation:'delete'}`
- [x] T055 [US3] Create `frontend/src/pages/EditContactPage.vue`: pre-fills form from Dexie contact; on save calls `useGeolocation()` then `contactStore.updateContact()`; validates name non-empty; navigates back to detail on success
- [x] T056 [US3] Update `frontend/src/pages/ContactDetailPage.vue`: wire Edit button to `/contacts/:id/edit`; wire Delete button to `contactStore.deleteContact()` with confirmation dialog ("All data will be irreversibly removed"); show `HistoryPanel` component (below)
- [x] T057 [US3] Create `frontend/src/components/HistoryPanel.vue`: renders `contact.history` as a table; each row shows field_name, old_value, new_value, changed_at, GPS (if available); shows "No history yet" when empty

**Checkpoint**: Run `pytest backend/contacts/tests/` → all pass. Edit a contact → history row appears in detail view. Delete contact → gone from list. GPS recorded in history when available.

---

## Phase 6: User Story 4 — Log an Interaction Entry (Priority: P3)

**Goal**: The user can add timestamped free-text notes per interaction. All entries for a contact form a reverse-chronological feed. Each entry stores GPS.

**Independent Test**: Add 3 interaction entries to a contact → all 3 appear in feed newest-first → GPS recorded on entries where permission granted → empty content rejected.

### Tests (write FIRST — must FAIL before implementation)

- [x] T058 [P] [US4] Write contract test for `POST /api/contacts/{contact_id}/interactions/` in `backend/contacts/tests/test_interactions_contract.py`: assert 201 with stored entry; 400 for blank content; 401 without session; 404 for unknown contact_id
- [x] T059 [P] [US4] Write contract test for `GET /api/contacts/{contact_id}/interactions/` in `backend/contacts/tests/test_interactions_contract.py`: assert 200 returns list ordered newest-first
- [x] T060 [P] [US4] Write integration test in `backend/contacts/tests/test_interactions.py`: add 3 entries → list ordered newest-first; entry with GPS stores coords; blank content returns 400

### Backend implementation

- [x] T061 [US4] Create `InteractionEntry` model in `backend/contacts/models.py` (UUID client PK, contact FK, content TextField, created_at immutable, updated_at auto, lat/lng nullable); generate migration
- [x] T062 [US4] Add `InteractionEntryIn`, `InteractionEntryOut` schemas to `backend/contacts/schemas.py`; update `ContactOut` to include `interaction_entries: list[InteractionEntryOut]`
- [x] T063 [US4] Implement `POST /api/contacts/{contact_id}/interactions/` and `GET /api/contacts/{contact_id}/interactions/` in `backend/contacts/router.py` (ordered by `-created_at`); validate content non-blank
- [x] T064 [US4] Add factory class for `InteractionEntry` in `backend/contacts/tests/factories.py`

### Frontend implementation

- [x] T065 [US4] Create interactionStore in `frontend/src/stores/interactions.ts`: state (entries: InteractionEntry[] per contact_id), action `createInteraction(contactId, content)` → captures GPS via `useGeolocation()` → writes to Dexie `interaction_entries` → adds outbox entry `{entity:'interaction_entry', operation:'create', payload}`
- [x] T066 [US4] Create `frontend/src/components/InteractionFeed.vue`: renders `interactionStore.entries` for current contact in reverse chronological order; each card shows content, created_at, GPS indicator (if available); "No interactions yet" empty state
- [x] T067 [US4] Create `frontend/src/components/AddInteractionForm.vue`: textarea + Save button; validates non-empty; calls `interactionStore.createInteraction()`; clears form on success
- [x] T068 [US4] Mount `InteractionFeed` and `AddInteractionForm` in `frontend/src/pages/ContactDetailPage.vue` below the history panel

**Checkpoint**: Run `pytest backend/contacts/tests/` → all pass. Open a contact detail → add interaction → feed updates immediately. GPS stored where available.

---

## Phase 7: User Story 5 — Manage Privacy Settings (Priority: P4)

**Goal**: The user can toggle GPS tracking on/off globally. When disabled, no location is captured for any future write. Re-enabling restores GPS capture. OS-denied permission falls back gracefully.

**Independent Test**: Disable GPS in settings → add a contact → contact has null GPS → re-enable → add another contact → GPS recorded.

### Tests (write FIRST — must FAIL before implementation)

- [x] T069 [P] [US5] Write contract test for `GET /api/settings/privacy/` and `PATCH /api/settings/privacy/` in `backend/settings_app/tests/test_privacy_contract.py`: assert GET returns current value; PATCH updates; 401 without session
- [x] T070 [P] [US5] Write integration test in `backend/settings_app/tests/test_privacy_integration.py`: disable GPS → POST /api/contacts/ with GPS payload → server ignores GPS (stores null) when location_tracking_enabled=False

### Backend implementation

- [x] T071 [US5] Add `PrivacySettingsOut` and `PrivacySettingsPatch` schemas to `backend/settings_app/schemas.py`
- [x] T072 [US5] Implement `GET /api/settings/privacy/` and `PATCH /api/settings/privacy/` in `backend/settings_app/router.py`; add router to `backend/crm/api.py` under `/settings/`
- [x] T073 [US5] Update `POST /api/contacts/` and `PATCH /api/contacts/{id}/` in `backend/contacts/router.py` to ignore GPS coordinates in the payload when `request.user.privacysettings.location_tracking_enabled == False`

### Frontend implementation

- [x] T074 [US5] Update settingsStore in `frontend/src/stores/settings.ts`: add `update(enabled: boolean)` action → calls `PATCH /api/settings/privacy/` → updates local state + Dexie `privacy_settings` table
- [x] T075 [US5] Create `frontend/src/pages/SettingsPage.vue`: toggle switch for "Record location with contacts and interactions"; shows current state from settingsStore; calls `settingsStore.update()` on change; adds router entry `/settings`

**Checkpoint**: Run `pytest backend/settings_app/tests/` → all pass. Toggle off GPS in UI → add contact → no GPS stored. Toggle back on → GPS stored.

---

## Phase 8: User Story 6 — Explore Contacts on a Map (Priority: P4)

**Goal**: Contacts and interaction entries with GPS coordinates are plotted as clustered pins on a map. Tapping a pin opens the associated contact.

**Independent Test**: Seed contacts and interactions with GPS → open `/map` → pins visible at correct locations → clusters shown for nearby pins with count → tap pin → navigate to contact detail.

### Tests (write FIRST — must FAIL before implementation)

- [x] T076 [P] [US6] Write contract test for `GET /api/map/pins/` in `backend/contacts/tests/test_map_contract.py`: assert 200 returns list of pins with lat/lng/type/contact_id/contact_name; contacts without GPS omitted; interaction entries with GPS included
- [x] T077 [P] [US6] Write integration test in `backend/contacts/tests/test_map_integration.py`: seed 3 contacts (2 with GPS, 1 without) and 2 interaction entries (both with GPS) → response contains exactly 4 pins
- [x] T078 [P] [US6] Write unit test for `MapPage.vue` in `frontend/src/pages/tests/MapPage.spec.ts`: map renders pins from store; clicking pin navigates to contact detail

### Backend implementation

- [x] T079 [US6] Implement `GET /api/map/pins/` in `backend/contacts/router.py`: query all active Contacts with non-null `created_lat` + all InteractionEntries with non-null `lat`; serialize each as `{type, id, contact_id, contact_name, lat, lng, label, timestamp}`; add router to `backend/crm/api.py` under `/map/`
- [x] T080 [US6] Add `MapPinOut` schema to `backend/contacts/schemas.py`

### Frontend implementation

- [x] T081 [US6] Fix Leaflet default marker icon paths for Vite in `frontend/src/main.ts`: `L.Icon.Default.mergeOptions()` with imported PNG assets
- [x] T082 [US6] Import Leaflet + markercluster CSS in `frontend/src/main.ts`: `leaflet/dist/leaflet.css`, `leaflet.markercluster/dist/MarkerCluster.css`, `leaflet.markercluster/dist/MarkerCluster.Default.css`
- [x] T083 [US6] Create `frontend/src/stores/map.ts` Pinia store: action `loadPins()` → fetches `GET /api/map/pins/` → stores pins array
- [x] T084 [US6] Create `frontend/src/pages/MapPage.vue`: `<l-map>` + `<l-tile-layer>` (OSM tiles, no API key); on `onMounted`, create `L.markerClusterGroup()`, iterate `mapStore.pins`, add `L.marker([lat, lng])` with `on('click', () => router.push('/contacts/' + pin.contact_id))`; add cluster layer to map; show empty state if no pins
- [x] T085 [US6] Add Map nav link to `frontend/src/App.vue` navigation bar

**Checkpoint**: Run `pytest backend/contacts/tests/test_map_*.py` → all pass. Open `/map` → pins visible → clusters shown for overlapping locations → tap pin → navigate to contact.

---

## Phase 9: Sync (Offline-First & Backend Sync)

**Purpose**: Wire the SyncService to the real pull/push endpoints. After this phase, the app works fully offline and syncs automatically when reconnected.

**⚠️ Depends on**: All data models from Phases 3–8 must exist before sync endpoints are implemented.

### Tests (write FIRST — must FAIL before implementation)

- [x] T086 [P] Write contract test for `GET /api/sync/pull/?since=` in `backend/sync/tests/test_sync_contract.py`: assert 200 with contacts, interaction_entries, contact_history, tombstones, server_time; only records with `updated_at > since` returned; tombstones include soft-deleted contacts
- [x] T087 [P] Write contract test for `POST /api/sync/push/` in `backend/sync/tests/test_sync_contract.py`: assert 200 with applied + errors arrays; create/update/delete operations applied; partial success (one error does not block others)
- [x] T088 [P] Write integration test in `backend/sync/tests/test_sync_integration.py`: create contact offline (in DB without sync) → pull returns it; push create → contact persisted; push delete → contact soft-deleted; push update with GPS → ContactHistory created

### Backend implementation

- [x] T089 Implement `GET /api/sync/pull/` in `backend/sync/router.py`: filter all entities by `updated_at > since`; include soft-deleted contacts as tombstones; return `server_time = now()`; use `AllObjectsManager` (unfiltered) for contacts; add router to `backend/crm/api.py` under `/sync/`
- [x] T090 [P] Implement `POST /api/sync/push/` in `backend/sync/router.py`: iterate `changes` array; for each `create` → create record (ignore 409 duplicate); `update` → update fields + generate ContactHistory; `delete` → soft-delete; return `applied` and `errors` lists
- [x] T091 [P] Add sync schemas to `backend/sync/schemas.py`: `OutboxChangeIn`, `SyncPushIn`, `SyncPullOut`, `SyncAppliedItem`, `SyncPushOut`, `TombstoneOut`
- [x] T092 [P] Create Django management command `backend/contacts/management/commands/purge_tombstones.py`: hard-deletes contacts where `deleted_at < now() - 30 days`; log count purged

### Frontend implementation

- [x] T093 Implement `SyncService.syncCycle()` in `frontend/src/services/sync.ts`: (1) read `last_sync_at` from localStorage; (2) call `GET /api/sync/pull/?since=last_sync_at` → upsert results into Dexie, remove tombstone IDs, update `last_sync_at` to `server_time`; (3) read all `outbox` entries with `synced=false`; (4) call `POST /api/sync/push/` with batched changes; (5) mark `synced=true` for applied entries; handle 401 (redirect to login without discarding outbox); log errors without throwing
- [x] T094 [P] Add sync status indicator (syncing spinner / last synced time / offline badge) to `frontend/src/App.vue` using a `syncStatus` ref updated by SyncService

**Checkpoint**: Run `pytest backend/sync/tests/` → all pass. Create contact offline (network tab disabled) → outbox entry visible in Dexie → re-enable network → sync cycle runs → contact appears on server.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final hardening, validation, and documentation. No new features.

- [x] T095 [P] Add SQLite WAL mode activation in `backend/crm/settings/base.py` via `OPTIONS: {'init_command': 'PRAGMA journal_mode=WAL'}` in DATABASES config
- [x] T096 [P] Add `AllObjectsManager` (unfiltered) to `Contact` model in `backend/contacts/models.py` for use by sync endpoints (alongside default `ActiveContactManager`)
- [x] T097 [P] Add `db_index=True` to `Contact.updated_at`, `InteractionEntry.updated_at` in `backend/contacts/models.py` for sync pull query performance; generate migration
- [x] T098 [P] Write end-to-end validation test in `backend/tests/test_e2e_flow.py`: full user journey via TestClient — register → add contact with GPS → verify GPS stored → disable GPS → add contact → verify no GPS → enable GPS → add interaction → verify GPS on interaction → sync pull returns all records → delete contact → tombstone in pull → purge_tombstones command removes tombstone after 30 days (mocked time)
- [x] T099 [P] Run quickstart.md validation: `docker compose up --build` → create superuser → add contact → search → edit → map view → `docker compose down` — manually confirm all steps work end-to-end
- [x] T100 [P] Security hardening: add `SECURE_BROWSER_XSS_FILTER`, `X_FRAME_OPTIONS`, `SECURE_CONTENT_TYPE_NOSNIFF` to `backend/crm/settings/production.py`; verify CSRF protection on all mutation endpoints

**Checkpoint**: All 100 tasks complete. Full user journey validated via docker-compose. All pytest and vitest suites pass.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — BLOCKS all user stories
- **Phases 3–8 (User Stories)**: All depend on Phase 2; can proceed in priority order (P1→P2→P3→P4) or in parallel if capacity allows
- **Phase 9 (Sync)**: Depends on all data models from Phases 3–8 being complete (all models must exist for sync endpoints)
- **Phase 10 (Polish)**: Depends on Phases 1–9

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories — first to implement
- **US2 (P2)**: Reads Contact data from US1 — independently testable but builds on US1 models
- **US3 (P3)**: Adds ContactHistory to Contact from US1 — requires US1 models
- **US4 (P3)**: Adds InteractionEntry to Contact from US1 — independent of US2 and US3
- **US5 (P4)**: PrivacySettings model exists from Phase 2 — API + UI are the only new additions; independent of US2–US4
- **US6 (P4)**: Reads GPS fields from Contact (US1) and InteractionEntry (US4) — must complete US1 and US4 first

### Within Each User Story

1. Write tests → confirm they FAIL (Red)
2. Create models + migrations
3. Create schemas
4. Implement API endpoints
5. Create Pinia store actions + Dexie writes
6. Implement Vue components / pages
7. Wire navigation
8. Confirm tests PASS (Green)
9. Refactor if needed
10. Commit (one commit per logical unit per constitution Principle VI)

---

## Parallel Opportunities

### Phase 1 (T003–T011)
T003, T004, T005, T006, T007, T008, T010, T011 can all run in parallel after T001–T002.

### Phase 2 (T012–T026)
- T012, T013 (tests) in parallel
- T014, T015, T016, T017, T018, T019, T020, T021, T023, T024, T025 in parallel after T014 (Ninja assembly T014 must precede T017)

### Phase 3 (US1)
- T027, T028, T029, T030 (tests) in parallel
- T031, T032 in parallel; T033 after T031+T032; T034 in parallel with T033
- T035 after T031 (Dexie mirrors Django models); T036 after T035

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (auth, Dexie, SyncService scaffold)
3. Complete Phase 3: US1 — Add Contact
4. **STOP and VALIDATE**: add contact → Dexie entry created → outbox queued
5. Deploy MVP for daily use

### Incremental Delivery

| Milestone | User Stories | Value Delivered |
|---|---|---|
| MVP | US1 | Add contacts with GPS |
| M2 | + US2 | Find and browse contacts |
| M3 | + US3, US4 | Track changes and log meetings |
| M4 | + US5, US6 | Privacy control + map view |
| M5 | + Sync (Phase 9) | True offline-first with sync |

---

## Notes

- TDD is non-negotiable per Constitution Principle V. Tests must exist and fail before each implementation block.
- Each task = one atomic commit per Constitution Principle VI. Never bundle unrelated changes.
- `[P]` tasks operate on different files with no shared dependencies within the same phase.
- All `[Story]` labels map to the acceptance scenarios in `spec.md` for traceability.
- Soft-delete tombstone behaviour (Phase 9) is documented as a justified complexity in `plan.md`.
- The Sync phase (Phase 9) intentionally comes after all data models are settled to avoid costly migration rework.
