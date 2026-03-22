---

description: "Task list template for feature implementation"
---

# Tasks: Add README with Installation & Deployment Documentation

**Input**: Design documents from `/specs/005-add-readme-docs/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, quickstart.md ✅

**Tests**: No automated tests — this is a documentation feature. Verification is manual (follow the instructions, confirm the app runs).

**Organization**: Tasks are grouped by user story. All tasks write to a single file (`README.md`), so they are sequential within each phase.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)

---

## Phase 1: Setup

**Purpose**: Create the README.md file with its top-level structure.

- [x] T001 Create `README.md` at the repository root with the document title, a one-line project description, and a table of contents linking to all major sections

**Checkpoint**: README.md exists at repo root and is renderable.

---

## Phase 2: User Story 1 — New Developer Sets Up Local Environment (Priority: P1) 🎯 MVP

**Goal**: A developer with Docker installed can clone the repo, follow the README, and have the full local dev environment running with hot-reload in under 15 minutes.

**Independent Test**: Follow only the local dev section of README.md on a clean machine; verify `http://localhost:5173` and `http://localhost:8000` are accessible and a code change triggers hot-reload.

### Implementation for User Story 1

- [x] T002 [US1] Write the **Prerequisites** section in `README.md`: list Docker (≥20.10) and Docker Compose v2 as requirements; note that ports 8000 and 5173 must be free
- [x] T003 [US1] Write the **Local Development** section in `README.md`: step-by-step commands to clone the repo, start the stack with `docker compose -f docker-compose.dev.yml up`, and access the frontend (port 5173) and backend (port 8000)
- [x] T004 [US1] Add hot-reload note to the Local Development section: explain that frontend (Vite HMR) and backend (Django dev server) both reload automatically on file changes via volume mounts
- [x] T005 [US1] Add teardown/reset instructions to the Local Development section: `docker compose -f docker-compose.dev.yml down` and the `-v` flag to remove named volumes for a clean slate

**Checkpoint**: A developer can get a working local environment by following only the README. User Story 1 is independently verifiable.

---

## Phase 3: User Story 2 — System Administrator Deploys to Production (Priority: P2)

**Goal**: A sysadmin can deploy the application to a Linux server with Docker, configure required environment variables, and confirm data persists across container restarts — following only the README.

**Independent Test**: Follow only the production deployment section on a clean Linux server; verify the app is accessible on `http://localhost:8000` and that data survives a `docker compose restart`.

### Implementation for User Story 2

- [x] T006 [US2] Write the **Production Deployment** section in `README.md`: step-by-step instructions to clone the repo, create a `.env` file (or export env vars), build and start the container with `docker compose up -d`, and verify with `curl http://localhost:8000`
- [x] T007 [US2] Write the **Environment Variables** reference table in `README.md` documenting all four variables (`SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `DATABASE_PATH`) with required/optional status, default value, and description (use content from `specs/005-add-readme-docs/quickstart.md`)
- [x] T008 [US2] Write the **Data Persistence** note in the Production Deployment section: explain that the `./data` directory is host-mounted into the container, the SQLite database lives at `./data/db.sqlite3`, and data survives container restarts and image rebuilds

**Checkpoint**: A sysadmin can deploy to production by following only the README. User Story 2 is independently verifiable.

---

## Phase 4: User Story 3 — Sysadmin Configures Reverse Proxy (Priority: P3)

**Goal**: A sysadmin running Apache2 or Nginx can configure a reverse proxy to the application container using a ready-to-use config snippet from the README.

**Independent Test**: Apply the config from the README to a web server in front of the running container; verify the app is accessible via the server's public domain name on port 80 (and 443 if HTTPS is configured).

### Implementation for User Story 3

- [x] T009 [US3] Write the **Reverse Proxy — Apache2** section in `README.md`: include the required `a2enmod proxy proxy_http` command, an HTTP VirtualHost config snippet with `ProxyPass` / `ProxyPassReverse` directives targeting `http://127.0.0.1:8000/`, and an HTTPS VirtualHost variant with SSL certificate paths (use content from `specs/005-add-readme-docs/research.md` Decision 5)
- [x] T010 [US3] Write the **Reverse Proxy — Nginx** section in `README.md`: include an HTTP `server` block with `proxy_pass http://127.0.0.1:8000` and appropriate `proxy_set_header` directives, plus a note on adding SSL (use content from `specs/005-add-readme-docs/research.md` Decision 6)
- [x] T011 [US3] Write the **CSRF Configuration** note in the Reverse Proxy section: explain that `CSRF_TRUSTED_ORIGINS` must be set to `https://yourdomain.com` when the application is served over HTTPS behind a proxy

**Checkpoint**: A sysadmin can configure both Apache2 and Nginx reverse proxies by following only the README. User Story 3 is independently verifiable.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final accuracy pass and edge case coverage.

- [x] T012 Add edge case notes to `README.md`: (a) in the Prerequisites section note what happens if ports 8000 or 5173 are in use; (b) in the Environment Variables table, highlight which variables are required and what the consequence is if `SECRET_KEY` or `CSRF_TRUSTED_ORIGINS` are left at their insecure defaults in production
- [x] T013 Review the complete `README.md` for accuracy against the actual `docker-compose.yml`, `docker-compose.dev.yml`, and `Dockerfile` — confirm all commands, port numbers, env var names, and file paths are correct
- [x] T014 Verify the rendered Markdown: confirm all headings, code blocks, and tables display correctly on GitHub (or equivalent); fix any formatting issues

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **User Stories (Phases 2–4)**: Depend on Phase 1; can proceed in priority order
- **Polish (Phase 5)**: Depends on all user story phases being complete

### User Story Dependencies

- **US1 (P1)**: Can start after T001 — no dependencies on US2 or US3
- **US2 (P2)**: Can start after T001 — no dependencies on US1 or US3
- **US3 (P3)**: Can start after T001 — no dependencies on US1 or US2

Note: All tasks write to the same file (`README.md`), so parallel execution within a session is not practical. Recommended approach: sequential, in priority order (US1 → US2 → US3).

### Within Each User Story

- Write the section content → verify accuracy → commit
- Each story's section is self-contained in the README

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001)
2. Complete Phase 2: User Story 1 (T002–T005)
3. **STOP and VALIDATE**: Follow the local dev instructions on a clean machine
4. Proceed to US2 and US3 once US1 is verified

### Incremental Delivery

1. T001 → README.md skeleton
2. T002–T005 → Local dev section complete → Independently testable
3. T006–T008 → Production deployment section complete → Independently testable
4. T009–T011 → Reverse proxy section complete → Independently testable
5. T012–T014 → Polish and final verification

---

## Notes

- No [P] markers: all tasks write to the same file and should be sequential
- [Story] labels map tasks to user stories for traceability
- No automated tests: verification is done by following the instructions
- Commit after each user story phase (e.g., after T005, T008, T011, T014)
- Content for env vars table is in `specs/005-add-readme-docs/quickstart.md`
- Content for proxy config snippets is in `specs/005-add-readme-docs/research.md`
