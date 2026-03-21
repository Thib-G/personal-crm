# personal-crm Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-21

## Active Technologies
- TypeScript 5 / Vue 3 (frontend only) + Vue 3 reactive system (ref, computed), Pinia (already present — not used for this feature per research Decision 1), @vue/test-utils + Vitest (tests) (002-sync-status-indicator)
- N/A — transient in-memory reactive state only (002-sync-status-indicator)
- Python 3.13 + Django 5.2 LTS (built-in `django.contrib.admin` — no new packages) (003-admin-contacts)
- SQLite via Django ORM (no schema changes — no migrations needed) (003-admin-contacts)

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
- 003-admin-contacts: Added Python 3.13 + Django 5.2 LTS (built-in `django.contrib.admin` — no new packages)
- 002-sync-status-indicator: Added TypeScript 5 / Vue 3 (frontend only) + Vue 3 reactive system (ref, computed), Pinia (already present — not used for this feature per research Decision 1), @vue/test-utils + Vitest (tests)

- 001-personal-crm: Added Python 3.13 (backend) · Node 22 / TypeScript 5 (frontend build) + Django 5.2 LTS, Django-Ninja ≥1.3, gunicorn, WhiteNoise ≥6, Dexie.js, Pinia, Vue Router 4, Leaflet.js, @vue-leaflet/vue-leaflet, Leaflet.markercluster

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
