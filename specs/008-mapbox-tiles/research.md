# Research: Mapbox Tiles with Leaflet

**Feature**: 008-mapbox-tiles
**Date**: 2026-03-25

---

## Decision 1: Tile Library — Keep Leaflet, Use Mapbox Raster Tiles

**Decision**: Retain the existing Leaflet.js map library. Use Mapbox's raster tile HTTP API instead of switching to Mapbox GL JS.

**Rationale**: The project already uses Leaflet with marker clustering. Mapbox GL JS is a full replacement library (heavier, different API surface, would require rewriting the entire MapPage). Mapbox exposes a standard XYZ-compatible raster tile endpoint that Leaflet can consume with a one-line URL change — minimal diff, zero new dependencies.

**Alternatives considered**:
- **Mapbox GL JS**: Full-featured vector tile renderer. Rejected — replaces Leaflet entirely, adding ~500 KB, rewrite cost, and API surface change. Violates Simplicity principle.
- **MapTiler**: Alternative hosted tile provider. Rejected — user specifically requested Mapbox.

---

## Decision 2: Mapbox Tile URL Format

**Decision**: Use Mapbox Styles API raster tile endpoint:

```
https://api.mapbox.com/styles/v1/mapbox/{style}/tiles/256/{z}/{x}/{y}{r}?access_token={token}
```

Where:
- `{style}` = one of `light-v11`, `dark-v11`, `satellite-streets-v12`
- `{r}` = Leaflet's retina placeholder — Leaflet substitutes `@2x` on high-DPI displays when `detectRetina: true`
- `{token}` = Mapbox access token from environment variable

**Retina support**: Leaflet's `L.tileLayer` supports a `{r}` URL token and a `detectRetina: true` option. When the device pixel ratio is ≥2, Leaflet inserts `@2x` into the URL, fetching the double-resolution tile variant that Mapbox serves natively. No extra code required.

**Tile size**: Using 256px tiles (not 512px) to avoid requiring `zoomOffset: -1` which changes zoom behavior. The `@2x` retina variant delivers the equivalent of a 512px tile at double pixel density.

**Alternatives considered**:
- 512px tiles with `zoomOffset: -1`: More common in some guides. Rejected — changes perceived zoom levels and complicates attribution.

---

## Decision 3: Tile Style Switcher UI

**Decision**: Implement a native Leaflet `L.Control` with three buttons (Light / Dark / Satellite) positioned top-right on the map. Replace the active tile layer on click; style the active button to indicate current selection.

**Rationale**: Leaflet's control system is idiomatic for map UI elements. It handles z-index, positioning, and event propagation correctly within the map canvas. No external dependencies.

**Alternatives considered**:
- Pinia store for selected style: Rejected — tile style is transient, session-only, no need for app-wide reactive state. Local `ref` in the component suffices.
- External buttons outside the map div: Rejected — breaks spatial affordance and requires extra layout work.

---

## Decision 4: Environment Variable

**Decision**: Use `VITE_MAPBOX_TOKEN` as the environment variable name for the Mapbox access token.

**Rationale**: Follows the existing project convention (`VITE_API_TARGET`). Vite exposes `VITE_`-prefixed variables to the browser bundle via `import.meta.env`. The token is a public-facing key (Mapbox access tokens are not server secrets — they're embedded in browser requests by design and scoped to a domain/URL via Mapbox dashboard restrictions).

**Dev**: Pass `VITE_MAPBOX_TOKEN` in `docker-compose.dev.yml` frontend service environment block. Developers set it in a `.env` file or shell environment.

**Prod**: Pass `VITE_MAPBOX_TOKEN=${VITE_MAPBOX_TOKEN}` as a build-time arg in the production Dockerfile/compose. The value is baked into the frontend static bundle at build time (Vite inlines `import.meta.env` at build).

**Note on security**: Mapbox tokens embedded in browser apps are intentionally scoped and rate-limited via Mapbox's token management (allowed URLs). This is the standard pattern for all Mapbox web SDK integrations. The token is not a private server-side secret.

**Alternatives considered**:
- Backend-proxied tiles: Rejected — adds backend complexity and latency; Mapbox tokens are designed for browser exposure.
- Runtime injection via Django template: Rejected — adds backend/frontend coupling; VITE_ build-time pattern is established in this project.

---

## Decision 5: Error Handling for Missing Token

**Decision**: At `onMounted`, check `import.meta.env.VITE_MAPBOX_TOKEN`. If falsy, set `errorMessage` with a clear configuration message ("Map tiles unavailable: VITE_MAPBOX_TOKEN is not configured") and return early without initialising the map.

**Rationale**: Consistent with existing error handling pattern in `MapPage.vue` (lines 61, 67). Visible failure is required by FR-007 and constitutionally mandated (Data Integrity: no silent failures).

---

## Mapbox Style Identifiers

| Style | Mapbox Style ID |
|-------|-----------------|
| Light (default) | `mapbox/light-v11` |
| Dark | `mapbox/dark-v11` |
| Satellite | `mapbox/satellite-streets-v12` |

---

## Files to Modify

| File | Change |
|------|--------|
| `frontend/src/pages/MapPage.vue` | Replace OSM tile layer; add Mapbox tiles with retina; add style switcher control |
| `frontend/src/vite-env.d.ts` | Add `VITE_MAPBOX_TOKEN: string` to `ImportMetaEnv` |
| `docker-compose.dev.yml` | Add `VITE_MAPBOX_TOKEN` to frontend service environment |
| `docker-compose.yml` | Add `VITE_MAPBOX_TOKEN` build arg / environment for the frontend build step |
| `frontend/.env.example` (new) | Document `VITE_MAPBOX_TOKEN=your-token-here` |

**No backend changes required.** No new npm packages required.
