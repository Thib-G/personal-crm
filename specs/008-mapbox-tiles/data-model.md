# Data Model: Mapbox Tiles

**Feature**: 008-mapbox-tiles
**Date**: 2026-03-25

---

## Overview

This feature has no persistent data model changes. All entities are transient, in-memory, frontend-only.

---

## Transient Entities

### TileStyle

Represents a selectable map tile configuration.

| Field | Type | Values | Notes |
|-------|------|--------|-------|
| id | string | `'light'`, `'dark'`, `'satellite'` | Unique identifier |
| label | string | `'Light'`, `'Dark'`, `'Satellite'` | Display label for UI control |
| styleId | string | `'mapbox/light-v11'`, `'mapbox/dark-v11'`, `'mapbox/satellite-streets-v12'` | Mapbox style path in tile URL |

**Default**: `'light'`

**Lifecycle**: Instantiated once at component mount; reset to default on page reload. Not persisted to IndexedDB, localStorage, or backend.

---

## Environment Configuration

### VITE_MAPBOX_TOKEN

| Property | Value |
|----------|-------|
| Variable name | `VITE_MAPBOX_TOKEN` |
| Scope | Frontend build-time (Vite inlines at compile) |
| Consumed by | `MapPage.vue` via `import.meta.env.VITE_MAPBOX_TOKEN` |
| Required | Yes — map will show error and not initialise if absent |
| Format | Mapbox public access token (`pk.eyJ1...`) |

---

## No Schema Changes

No Django migrations required. No IndexedDB schema changes required.
