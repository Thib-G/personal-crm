# Quickstart: Personal CRM

**Prerequisite**: Docker and Docker Compose installed on a Linux/macOS host.

---

## Run Locally (Development)

### 1. Clone and configure

```bash
git clone <repo-url> personal-crm
cd personal-crm
cp backend/.env.example backend/.env
# Edit backend/.env — set SECRET_KEY, DEBUG=True, ALLOWED_HOSTS=localhost
```

### 2. Start with Docker Compose

```bash
docker compose up --build
```

This starts one container: the Django app (gunicorn) serving both the API and the pre-built Vue SPA.

The app is available at **http://localhost:8000**.

### 3. Create the admin user (first run only)

```bash
docker compose exec app python manage.py createsuperuser
```

Then open http://localhost:8000 and log in.

---

## Development Without Docker

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API available at http://localhost:8000/api/docs (Django-Ninja auto-docs).

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Vue dev server at http://localhost:5173. Configure `vite.config.ts` to proxy `/api/` to `http://localhost:8000`.

---

## Run Tests

### Backend

```bash
cd backend
pytest
# With coverage:
pytest --cov=. --cov-report=term-missing
```

### Frontend

```bash
cd frontend
npx vitest run
# With UI:
npx vitest --ui
```

---

## Project Layout

```
personal-crm/
├── backend/
│   ├── crm/
│   │   ├── settings/
│   │   │   ├── base.py
│   │   │   └── production.py
│   │   ├── api.py            # NinjaAPI assembly — add_router calls
│   │   └── urls.py
│   ├── contacts/
│   │   ├── models.py
│   │   ├── schemas.py
│   │   └── router.py
│   ├── sync/
│   │   ├── router.py
│   │   └── schemas.py
│   ├── users/
│   │   ├── router.py
│   │   └── schemas.py
│   ├── conftest.py
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── stores/           # Pinia stores
│   │   ├── services/
│   │   │   ├── db.ts         # Dexie IndexedDB schema
│   │   │   └── sync.ts       # SyncService (outbox + delta sync)
│   │   └── composables/
│   ├── tests/
│   └── vite.config.ts
├── specs/
│   └── 001-personal-crm/
│       ├── plan.md
│       ├── research.md
│       ├── data-model.md
│       ├── quickstart.md     # This file
│       └── contracts/
│           └── api.md
├── Dockerfile
└── docker-compose.yml
```

---

## Production Deployment (VPS + Apache2)

### 1. Build and push the image

```bash
docker build --platform linux/amd64 -t personal-crm:latest .
```

### 2. On the VPS

```bash
git pull
docker compose up -d --build
```

### 3. Apache2 virtual host (Debian 13)

```apache
<VirtualHost *:443>
    ServerName crm.yourdomain.com
    SSLEngine on
    # certbot/Let's Encrypt SSL directives

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

Enable required Apache modules: `proxy`, `proxy_http`, `ssl`, `headers`.

### 4. SQLite backup (cron on host)

```bash
# /etc/cron.daily/crm-backup
sqlite3 /path/to/data/db.sqlite3 ".backup /backups/crm-$(date +%F).sqlite3"
```

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SECRET_KEY` | Yes | Django secret key — generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | No | `True` for local dev; `False` (default) in production |
| `ALLOWED_HOSTS` | Yes (prod) | Comma-separated hostnames, e.g. `crm.yourdomain.com` |
| `DJANGO_SETTINGS_MODULE` | No | Defaults to `crm.settings.base`; use `crm.settings.production` in Docker |
| `DATABASE_PATH` | No | Path to SQLite file, default `./data/db.sqlite3` |
