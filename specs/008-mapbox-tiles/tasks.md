# Tasks: Mapbox Tile Integration

**Input**: Design documents from `/specs/008-mapbox-tiles/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅

**Tests**: Included — TDD is mandatory per project constitution (Principle V).

**Organization**: Tasks grouped by user story. Each story is independently implementable and testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths included in all descriptions

## Path Conventions

Web application layout:
- Frontend: `frontend/src/`
- Compose: `docker-compose.dev.yml`, `docker-compose.yml`, `Dockerfile`
- Docs: `README.md`, `frontend/.env.example`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Type system foundation that all stories depend on

- [x] T001 Add `VITE_MAPBOX_TOKEN: string` to `ImportMetaEnv` interface in `frontend/src/vite-env.d.ts`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No additional foundational work beyond T001 — this is a frontend-only, single-file change feature. T001 in Phase 1 covers the only true prerequisite.

**⚠️ CRITICAL**: Phase 1 (T001) must be complete before user story implementation begins

---

## Phase 3: User Story 1 — Mapbox Light Tiles with Retina (Priority: P1) 🎯 MVP

**Goal**: Replace OSM tiles with Mapbox light-v11 tiles. Automatically serve 2x retina tiles on HiDPI screens. Guard against missing token with a visible error.

**Independent Test**: Open the map in a browser — Mapbox light tiles appear instead of OSM tiles. On a retina screen, tiles are crisp. If `VITE_MAPBOX_TOKEN` is unset, a visible error message is shown and the map does not initialise.

### Tests for User Story 1

> **Write these tests FIRST — they MUST FAIL before implementation begins (Red)**

- [x] T002 [US1] Create `frontend/src/pages/tests/MapPage.spec.ts` with a failing test: when `VITE_MAPBOX_TOKEN` is empty, `errorMessage` contains "VITE_MAPBOX_TOKEN" and `L.map` is NOT called
- [x] T003 [US1] Add failing test in `frontend/src/pages/tests/MapPage.spec.ts`: when token is set, `L.tileLayer` is called with a URL containing `light-v11` and options `{ detectRetina: true }`

### Implementation for User Story 1

- [x] T004 [US1] Add token guard at top of `onMounted` in `frontend/src/pages/MapPage.vue`: read `import.meta.env.VITE_MAPBOX_TOKEN`; if falsy, set `errorMessage` and return early (makes T002 pass)
- [x] T005 [US1] Replace OSM `L.tileLayer` call in `frontend/src/pages/MapPage.vue` with Mapbox light-v11 URL `https://api.mapbox.com/styles/v1/mapbox/light-v11/tiles/256/{z}/{x}/{y}{r}?access_token={token}` and options `tileSize: 256, maxZoom: 22, detectRetina: true` plus Mapbox attribution (makes T003 pass)

**Checkpoint**: `npm run test` passes for MapPage. Map shows Mapbox light tiles with retina support. Missing token shows error.

---

## Phase 4: User Story 2 — Tile Style Switcher (Priority: P2)

**Goal**: Add a Light / Dark / Satellite switcher control on the map. Switching replaces the active tile layer immediately; no page reload required.

**Independent Test**: Open the map, click "Dark" → dark tiles load. Click "Satellite" → satellite imagery loads. Click "Light" → light tiles restored. Active button is visually distinct from inactive buttons.

### Tests for User Story 2

> **Write these tests FIRST — they MUST FAIL before implementation begins (Red)**

- [x] T006 [US2] Add failing tests in `frontend/src/pages/tests/MapPage.spec.ts`:
  - Clicking dark button → `L.tileLayer` called with URL containing `dark-v11`
  - Clicking satellite button → `L.tileLayer` called with URL containing `satellite-streets-v12`
  - After clicking dark, dark button has CSS class `active`; light button does not

### Implementation for User Story 2

- [x] T007 [US2] Define `TILE_STYLES` constant in `frontend/src/pages/MapPage.vue` mapping ids (`light`, `dark`, `satellite`) to Mapbox style paths and display labels
- [x] T008 [US2] Implement a custom `L.Control` in `frontend/src/pages/MapPage.vue` (position: `topright`) that renders three buttons (Light, Dark, Satellite) and tracks the active style
- [x] T009 [US2] Wire switcher button clicks in `frontend/src/pages/MapPage.vue`: remove current tile layer from map, add new `L.tileLayer` for selected style, update `active` CSS class on buttons (makes T006 tests pass)
- [x] T010 [US2] Add scoped CSS in `frontend/src/pages/MapPage.vue` for the switcher control: button group styling, active state highlight, z-index above map tiles

**Checkpoint**: All three tile styles switch correctly. Switcher is visible and styled. All tests pass.

---

## Phase 5: User Story 3 — Environment Variable Configuration (Priority: P3)

**Goal**: Wire `VITE_MAPBOX_TOKEN` through dev and production Docker environments. Document the setup in `.env.example` and README so any developer or operator can configure the token without reading source code.

**Independent Test**: Clone repo, set `VITE_MAPBOX_TOKEN` in `.env`, run `docker compose -f docker-compose.dev.yml up` — map loads with Mapbox tiles. Run without the env var — map shows error. README Mapbox section is present and accurate.

### Implementation for User Story 3

- [x] T011 [P] [US3] Add `VITE_MAPBOX_TOKEN=${VITE_MAPBOX_TOKEN}` to the `frontend` service `environment` block in `docker-compose.dev.yml`
- [x] T012 [P] [US3] Add `ARG VITE_MAPBOX_TOKEN` and `ENV VITE_MAPBOX_TOKEN=$VITE_MAPBOX_TOKEN` to the frontend build stage in `Dockerfile` (before the `npm run build` step)
- [x] T013 [P] [US3] Add `VITE_MAPBOX_TOKEN: ${VITE_MAPBOX_TOKEN}` under `build.args` for the app service in `docker-compose.yml`
- [x] T014 [P] [US3] Create `frontend/.env.example` with content: `VITE_MAPBOX_TOKEN=pk.your-mapbox-token-here` and a comment explaining the variable
- [x] T015 [US3] Add a "Mapbox Setup" section to `README.md` covering: (1) create a free Mapbox account and copy the default public token, (2) for dev — add `VITE_MAPBOX_TOKEN=pk.xxx` to a local `.env` file or export it in the shell, (3) for production — add it to the `.env` file read by `docker-compose.yml`

**Checkpoint**: `docker compose -f docker-compose.dev.yml up` uses the token from `.env`. README section is clear and self-contained.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup and final validation

- [x] T016 [P] Run `npm run test` in `frontend/` and confirm all tests pass (zero regressions in existing suites)
- [x] T017 [P] Run `npm run type-check` (or equivalent `vue-tsc`) in `frontend/` and confirm no TypeScript errors
- [x] T018 Delete the accidentally created `009-retina-tiles` branch: `git branch -d 009-retina-tiles`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (T001)**: No dependencies — start immediately
- **Phase 3 US1 (T002–T005)**: Depends on T001 — blocks nothing else
- **Phase 4 US2 (T006–T010)**: Depends on Phase 3 completion (switcher builds on the tile layer established in US1)
- **Phase 5 US3 (T011–T015)**: Independent of US1/US2 — can run in parallel with Phase 3 after T001
- **Phase 6 Polish (T016–T018)**: Depends on all stories complete

### User Story Dependencies

- **US1 (P1)**: After T001 — no other story dependencies
- **US2 (P2)**: After US1 — switcher replaces the tile layer set up in US1
- **US3 (P3)**: After T001 — fully independent of US1 and US2 (config/docs work)

### Within Each User Story

- Tests MUST be written and FAIL before implementation (constitution Principle V)
- T002 → T004 (test drives the guard)
- T003 → T005 (test drives the tile URL)
- T006 → T007 → T008 → T009 (tests drive switcher, styles needed before control)
- T011–T014 are independent of each other [P] within US3

### Parallel Opportunities

- T002 and T003 can be written in parallel (both in the same new test file, but logically independent)
- T011, T012, T013, T014 (US3 config tasks) can all run in parallel
- US3 (T011–T015) can run in parallel with US1 (T002–T005) after T001

---

## Parallel Example: User Story 3

```bash
# All four config tasks can run simultaneously:
Task T011: docker-compose.dev.yml  ← add env var
Task T012: Dockerfile              ← add ARG/ENV
Task T013: docker-compose.yml      ← add build arg
Task T014: frontend/.env.example   ← create file
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete T001: Add type to `vite-env.d.ts`
2. Complete T002–T003: Write failing tests
3. Complete T004–T005: Implement token guard + Mapbox tile URL
4. **STOP and VALIDATE**: Map shows Mapbox light tiles, retina works, missing-token error works
5. Optional: Wire env var (T011–T014) so it actually runs in Docker

### Incremental Delivery

1. T001 → T002–T005 (US1) → Map works with Mapbox ✅
2. T006–T010 (US2) → Style switcher works ✅
3. T011–T015 (US3) → Docker + README fully configured ✅
4. T016–T018 (Polish) → Clean, tested, branch deleted ✅

---

## Notes

- [P] tasks = different files, no blocking dependencies within their phase
- TDD is mandatory (constitution Principle V) — tests must fail before implementation
- `MapPage.spec.ts` does not yet exist — T002 creates it
- The `Dockerfile` frontend build stage must be identified before T012 (read the file first)
- Commit after each completed task or logical group (constitution Principle VI: Atomic Commits)
- Stop at each **Checkpoint** to validate the story independently before proceeding
