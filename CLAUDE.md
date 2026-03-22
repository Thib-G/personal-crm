# personal-crm Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-22

## Active Technologies
- TypeScript 5 / Vue 3 (frontend only) + Vue 3 reactive system (ref, computed), Pinia (already present — not used for this feature per research Decision 1), @vue/test-utils + Vitest (tests) (002-sync-status-indicator)
- N/A — transient in-memory reactive state only (002-sync-status-indicator)
- Python 3.13 + Django 5.2 LTS (built-in `django.contrib.admin` — no new packages) (003-admin-contacts)
- SQLite via Django ORM (no schema changes — no migrations needed) (003-admin-contacts)
- TypeScript 5 / Vue 3 + Vue 3 (built-in scoped styles) — no new packages (004-ui-layout)
- N/A — frontend-only, no data changes (004-ui-layout)
- Markdown (documentation-only deliverable) + N/A — no new packages; existing Docker Compose files and Dockerfile are the source of truth (005-add-readme-docs)
- N/A — no data changes (005-add-readme-docs)
- TypeScript 5 / Vue 3 + `dexie` (already installed — `liveQuery` is a named export, no new package needed), Pinia, Vue Router 4 (006-fix-sync-ui-refresh)
- IndexedDB via Dexie.js (no schema changes) (006-fix-sync-ui-refresh)

- Python 3.13 (backend) · Node 22 / TypeScript 5 (frontend build) + Django 5.2 LTS, Django-Ninja ≥1.3, gunicorn, WhiteNoise ≥6, Dexie.js, Pinia, Vue Router 4, Leaflet.js, @vue-leaflet/vue-leaflet, Leaflet.markercluster (001-personal-crm)

## Project Structure

```text
src/
tests/
```

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.13 (backend) · Node 22 / TypeScript 5 (frontend build): Follow standard conventions

## Recent Changes
- 006-fix-sync-ui-refresh: Added TypeScript 5 / Vue 3 + `dexie` (already installed — `liveQuery` is a named export, no new package needed), Pinia, Vue Router 4
- 005-add-readme-docs: Added Markdown (documentation-only deliverable) + N/A — no new packages; existing Docker Compose files and Dockerfile are the source of truth
- 004-ui-layout: Added TypeScript 5 / Vue 3 + Vue 3 (built-in scoped styles) — no new packages


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
