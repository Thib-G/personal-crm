# Implementation Plan: Mapbox Tile Integration

**Branch**: `008-mapbox-tiles` | **Date**: 2026-03-25 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/008-mapbox-tiles/spec.md`

## Summary

Replace the hardcoded OpenStreetMap tile layer in `MapPage.vue` with Mapbox raster tiles (light by default, plus dark and satellite variants). Add a tile style switcher control on the map. Support retina/HiDPI displays via Leaflet's native `detectRetina` option. Expose the Mapbox access token via a `VITE_MAPBOX_TOKEN` environment variable, following the existing `VITE_API_TARGET` pattern.

**No new npm packages. No backend changes. No schema changes.**

## Technical Context

**Language/Version**: TypeScript 5 / Node 22 (frontend build)
**Primary Dependencies**: Leaflet 1.9.4 (existing), Vite (existing), Vue 3 (existing)
**Storage**: N/A — no data persistence
**Testing**: Vitest + @vue/test-utils (existing)
**Target Platform**: Web browser (SPA); built to static assets served by Django/WhiteNoise
**Project Type**: Web application (frontend SPA change only)
**Performance Goals**: No tile load regression vs. OSM baseline; retina tiles load only on HiDPI screens
**Constraints**: No new dependencies; no backend changes; token must not appear in committed source files
**Scale/Scope**: Single-user; one map page

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Privacy-First | ✅ Pass | No contact data transmitted to Mapbox. Only map tile requests (z/x/y coordinates) are made — no PII. |
| II. Simplicity Over Features | ✅ Pass | Keeping Leaflet; no new packages. Minimal change: URL swap + env var + switcher control. |
| III. Data Integrity | ✅ Pass | No data model changes. Missing token surfaces a visible error (FR-007). |
| IV. User-Owned Data | ✅ Pass | No data storage changes. |
| V. TDD | ✅ Pass | Tests written before implementation per constitution. |
| VI. Atomic Commits | ✅ Pass | Tasks decomposed into discrete, independently committable units. |
| Stack Constraints | ✅ Pass | Vue 3 / TypeScript / Leaflet / Vite — all existing stack. |

**Gate: PASS** — proceed to implementation.

## Project Structure

### Documentation (this feature)

```text
specs/008-mapbox-tiles/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code Changes

```text
frontend/
├── .env.example                       # NEW — documents VITE_MAPBOX_TOKEN
├── src/
│   ├── pages/
│   │   └── MapPage.vue                # MODIFY — Mapbox tiles, switcher, retina
│   └── vite-env.d.ts                  # MODIFY — add VITE_MAPBOX_TOKEN type

docker-compose.dev.yml                 # MODIFY — add VITE_MAPBOX_TOKEN to frontend env
docker-compose.yml                     # MODIFY — add VITE_MAPBOX_TOKEN build arg
```

**Structure Decision**: Single-project frontend-only change. Backend untouched.

## Implementation Design

### 1. Tile URL Pattern

```
https://api.mapbox.com/styles/v1/{styleId}/tiles/256/{z}/{x}/{y}{r}?access_token={token}
```

- `{styleId}` — one of `mapbox/light-v11`, `mapbox/dark-v11`, `mapbox/satellite-streets-v12`
- `{r}` — Leaflet retina placeholder; becomes `@2x` on HiDPI screens when `detectRetina: true`
- `{token}` — value of `import.meta.env.VITE_MAPBOX_TOKEN`

Leaflet `L.tileLayer` options:
```
tileSize: 256
maxZoom: 22
detectRetina: true
attribution: '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
```

### 2. Tile Style Switcher

A custom `L.Control` (position: `topright`) renders three buttons: Light | Dark | Satellite.

- Active style button gets an `active` CSS class for visual feedback
- On click: remove the current `L.TileLayer` from the map, add the new one, update active state
- Default on mount: `light`

### 3. Token Guard

At the top of `onMounted`, before map initialisation:
```
const token = import.meta.env.VITE_MAPBOX_TOKEN
if (!token) {
  errorMessage.value = 'Map tiles unavailable: VITE_MAPBOX_TOKEN is not configured.'
  return
}
```

### 4. Environment Variable Wiring

**`frontend/src/vite-env.d.ts`** — extend `ImportMetaEnv`:
```typescript
interface ImportMetaEnv {
  readonly VITE_API_TARGET: string
  readonly VITE_MAPBOX_TOKEN: string
}
```

**`docker-compose.dev.yml`** — frontend service:
```yaml
environment:
  - VITE_API_TARGET=http://backend:8000
  - VITE_MAPBOX_TOKEN=${VITE_MAPBOX_TOKEN}
```

**`docker-compose.yml`** — app service build args (Vite bakes env into the static bundle):
```yaml
build:
  args:
    - VITE_MAPBOX_TOKEN=${VITE_MAPBOX_TOKEN}
```

**`frontend/.env.example`**:
```
VITE_MAPBOX_TOKEN=pk.your-mapbox-token-here
```

**`README.md`** — add a "Mapbox Setup" section covering:
- Where to create a Mapbox account and generate a public access token
- How to set `VITE_MAPBOX_TOKEN` for local development (shell export or `.env` file)
- How to set it for production (Docker Compose `.env` file or hosting environment variable)

## Testing Strategy

### Unit / Component Tests (Vitest + @vue/test-utils)

- **Token missing**: Mock `import.meta.env.VITE_MAPBOX_TOKEN = ''` → `errorMessage` contains "VITE_MAPBOX_TOKEN"
- **Token present**: Mock token → `L.tileLayer` called with Mapbox URL containing the token and `light-v11`
- **Style switcher — dark**: Click dark button → `L.tileLayer` called with `dark-v11`
- **Style switcher — satellite**: Click satellite button → `L.tileLayer` called with `satellite-streets-v12`
- **Retina option**: Verify `detectRetina: true` passed to every `L.tileLayer` call
- **Switcher active state**: After switching to dark, dark button has `active` class; light does not

All tests mock `leaflet` (already mocked in existing test setup per `tests/` patterns).

## Complexity Tracking

*No constitution violations — table not required.*
