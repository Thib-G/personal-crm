# README Structure Outline

**Feature**: 005-add-readme-docs | **Date**: 2026-03-22

This file defines the required sections and content of `README.md`. Use it as a writing guide during implementation.

---

## README.md Section Map

```
README.md
├── # Personal CRM
│   └── One-line description of the project
│
├── ## Prerequisites
│   ├── Docker (version requirement)
│   ├── Docker Compose v2 (version requirement)
│   └── Note on ports used (8000, 5173)
│
├── ## Local Development
│   ├── 1. Clone the repository
│   ├── 2. Start the stack
│   │   └── docker compose -f docker-compose.dev.yml up
│   ├── 3. Access the app
│   │   ├── Frontend: http://localhost:5173
│   │   └── Backend API: http://localhost:8000
│   ├── 4. Hot-reload note (automatic for both frontend and backend)
│   └── 5. Stopping / teardown
│       └── docker compose -f docker-compose.dev.yml down [-v to remove volumes]
│
├── ## Production Deployment
│   ├── 1. Clone the repository on the server
│   ├── 2. Configure environment variables
│   │   └── Required vars table: SECRET_KEY, ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS, DATABASE_PATH
│   ├── 3. Start the container
│   │   └── docker compose up -d
│   ├── 4. Verify the application is running
│   │   └── curl http://localhost:8000
│   └── 5. Data persistence note
│       └── Data stored in ./data/db.sqlite3 (host-mounted volume)
│
├── ## Web Server Reverse Proxy
│   ├── ### Apache2
│   │   ├── Required modules (mod_proxy, mod_proxy_http)
│   │   ├── HTTP VirtualHost config snippet
│   │   ├── HTTPS VirtualHost config snippet
│   │   └── Reload command: systemctl reload apache2
│   ├── ### Nginx
│   │   ├── HTTP server block config snippet
│   │   ├── HTTPS note
│   │   └── Reload command: systemctl reload nginx
│   └── ### CSRF Configuration
│       └── Set CSRF_TRUSTED_ORIGINS=https://yourdomain.com when using HTTPS
│
└── ## Environment Variables Reference
    └── Full table: variable, required/optional, default, description
```

---

## Environment Variables Reference Table (for README)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | insecure dev key | Django cryptographic secret key. Generate with `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `ALLOWED_HOSTS` | **Yes** | `localhost` | Comma-separated list of allowed hostnames. Must include your public domain in production. |
| `CSRF_TRUSTED_ORIGINS` | **Yes** | `http://localhost:8000` | Full URL(s) trusted for CSRF. Set to `https://yourdomain.com` when deployed with HTTPS. |
| `DATABASE_PATH` | No | `/app/data/db.sqlite3` | Path inside the container where SQLite database is stored. The `./data` directory is mounted from the host. |
| `DJANGO_SETTINGS_MODULE` | No | `crm.settings.production` | Django settings module. Do not change unless you know what you're doing. |
