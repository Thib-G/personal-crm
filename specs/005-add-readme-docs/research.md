# Research: Add README with Installation & Deployment Documentation

**Feature**: 005-add-readme-docs | **Date**: 2026-03-22

All decisions below are derived from reading the existing project files (`docker-compose.yml`, `docker-compose.dev.yml`, `Dockerfile`) and the project constitution. No external research was required.

---

## Decision 1: README file location and format

**Decision**: Single `README.md` at the repository root, written in GitHub-flavoured Markdown.

**Rationale**: Standard convention; GitHub, GitLab, and Gitea all render `README.md` automatically on the repository landing page. No alternative file name or location was viable.

**Alternatives considered**: `docs/README.md` or a MkDocs site — rejected as unnecessary complexity for a single-page reference document (violates Principle II).

---

## Decision 2: Reverse proxy web servers to document

**Decision**: Apache2 (primary) and Nginx (secondary).

**Rationale**: Apache2 is the project's constitutionally mandated reverse proxy on the production Debian 13 host. Nginx is included as a secondary reference per explicit user request, as many developers are more familiar with Nginx syntax.

**Alternatives considered**: Apache2 only — rejected by user. Caddy — not requested and not in use.

---

## Decision 3: Local dev setup method

**Decision**: `docker compose -f docker-compose.dev.yml up` using the existing `docker-compose.dev.yml`.

**Rationale**: The dev compose file runs the backend with Django's development server (hot-reload) and the frontend with Vite's dev server (HMR). This is the only supported local dev path.

**Key facts from `docker-compose.dev.yml`**:
- Backend: `http://localhost:8000` (Django dev server, hot-reload via volume mount)
- Frontend: `http://localhost:5173` (Vite HMR)
- Frontend accesses backend via `VITE_API_TARGET=http://backend:8000` (internal Docker DNS)
- Default env vars are pre-configured; no `.env` file required for local dev
- Node modules persisted in a named volume (`frontend_node_modules`) to avoid reinstalling on restart

---

## Decision 4: Production deployment method

**Decision**: `docker compose up` using `docker-compose.yml` (builds multi-stage Docker image).

**Rationale**: The production compose file builds a single image that includes the compiled Vue SPA as Django static files, served by gunicorn. The container binds to `127.0.0.1:8000` only, requiring the reverse proxy.

**Key facts from `docker-compose.yml` and `Dockerfile`**:
- Multi-stage build: Node 22 Alpine (Vue build) → Python 3.13 slim (Django runtime)
- Gunicorn: 2 workers, 2 threads, sync worker class, 30s timeout
- Port: `127.0.0.1:8000:8000` (localhost-only, not directly public)
- Data volume: `./data:/app/data` (host-mounted; SQLite lives at `/app/data/db.sqlite3`)
- `restart: unless-stopped` ensures the container survives server reboots

**Required environment variables** (from `docker-compose.yml`):
| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `SECRET_KEY` | Yes | insecure dev key | Must be changed in production; Django cryptographic key |
| `ALLOWED_HOSTS` | Yes | `localhost` | Must include the public domain in production |
| `DATABASE_PATH` | No | `/app/data/db.sqlite3` | Relative to container; default is safe |
| `CSRF_TRUSTED_ORIGINS` | Yes | `http://localhost:8000` | Must match the public HTTPS URL behind the proxy |

---

## Decision 5: Apache2 proxypass configuration pattern

**Decision**: Standard Apache2 `ProxyPass` / `ProxyPassReverse` directives in a VirtualHost block.

**Rationale**: The constitution specifies Apache2 on Debian 13. The configuration routes all traffic to the container on `127.0.0.1:8000`.

**Configuration pattern**:
```apache
<VirtualHost *:80>
    ServerName example.com

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

For HTTPS (recommended for production):
```apache
<VirtualHost *:443>
    ServerName example.com
    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/example.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/example.com/privkey.pem

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

Required Apache2 modules: `mod_proxy`, `mod_proxy_http` (enable with `a2enmod proxy proxy_http`).

**CSRF consideration**: When behind HTTPS, `CSRF_TRUSTED_ORIGINS` must be set to `https://example.com`.

---

## Decision 6: Nginx proxypass configuration pattern

**Decision**: Standard Nginx `proxy_pass` directive in a `server` block.

**Configuration pattern**:
```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

For HTTPS, add `listen 443 ssl` with certificate paths and set `CSRF_TRUSTED_ORIGINS=https://example.com`.

---

## Summary of Unknowns Resolved

All NEEDS CLARIFICATION markers were resolved during specification. No blocking unknowns remain:

- Web server scope: Apache2 + Nginx ✅
- README location: Repo root as `README.md` ✅
- All env vars documented ✅
- Dev vs production setup paths clearly differentiated ✅
