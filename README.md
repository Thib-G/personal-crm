# Personal CRM

A self-hosted personal contact relationship manager — runs entirely in Docker, stores data locally, and is accessible from any browser.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Web Server Reverse Proxy](#web-server-reverse-proxy)
- [Environment Variables Reference](#environment-variables-reference)

---

## Prerequisites

- **Docker** ≥ 20.10
- **Docker Compose** v2 (`docker compose`, not `docker-compose`)

> **Linux server note**: Docker Desktop (macOS/Windows) bundles Docker Compose automatically. On a Linux server you must install it separately:
> ```bash
> sudo apt-get update && sudo apt-get install docker-compose-plugin
> ```
> Verify with `docker compose version` before proceeding.

> **Port requirements**: The local development stack uses ports **8000** (backend) and **5173** (frontend). Make sure both are free before starting. If either port is in use, stop the conflicting process or edit `docker-compose.dev.yml` to use different host ports.

---

## Local Development

### 1. Clone the repository

```bash
git clone <repo-url>
cd personal-crm
```

### 2. Start the stack

```bash
docker compose -f docker-compose.dev.yml up
```

Docker will build the images on the first run. Subsequent starts are faster.

### 3. Access the application

| Service | URL |
|---------|-----|
| Frontend (Vue / Vite) | http://localhost:5173 |
| Backend API (Django) | http://localhost:8000 |

Open **http://localhost:5173** in your browser to use the application.

### 4. Hot-reload

Both services reload automatically when you edit source files — no restart needed:

- **Frontend**: Vite HMR picks up changes to files in `frontend/` instantly.
- **Backend**: Django's development server reloads when Python files in `backend/` change.

This works because both directories are mounted as volumes into their containers.

No `.env` file is needed for local development — safe default values are pre-configured in `docker-compose.dev.yml`.

### 5. Stopping and teardown

Stop the stack (keep data):

```bash
docker compose -f docker-compose.dev.yml down
```

Stop and remove all volumes (full reset, **deletes local dev data**):

```bash
docker compose -f docker-compose.dev.yml down -v
```

---

## Production Deployment

The production image is a single Docker container that bundles the compiled frontend and the Django backend, served by Gunicorn. The container binds to **localhost only** — a reverse proxy (Apache2 or Nginx) handles public traffic.

### 1. Clone the repository on the server

```bash
git clone <repo-url>
cd personal-crm
```

### 2. Configure environment variables

Create a `.env` file in the project root (this file is gitignored):

```bash
SECRET_KEY=<generate a strong random key — see Environment Variables Reference below>
ALLOWED_HOSTS=yourdomain.com
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

> **Security**: Never leave `SECRET_KEY` at its default value in production — the default is intentionally insecure and will expose your application to attacks. Generate a strong key with:
> ```bash
> python3 -c "import secrets; print(secrets.token_urlsafe(50))"
> ```

### 3. Start the container

```bash
docker compose up -d
```

This builds the production image (frontend + backend) and starts the container. The first build takes a few minutes. On subsequent deploys, only changed layers are rebuilt.

### 4. Create your user account

```bash
docker compose exec app python manage.py createsuperuser
```

Follow the prompts to set a username and password. This only needs to be done once — the account persists in the data volume.

### 5. Verify the application is running

```bash
curl http://localhost:8000
```

You should receive an HTTP response. The application is now running and waiting for the reverse proxy.

### 6. Data persistence

Application data is stored in `./data/db.sqlite3` on the **host machine** — it is mounted into the container at `/app/data/db.sqlite3`. This means:

- Data **survives** container restarts and image rebuilds.
- Backing up your data is as simple as copying the `./data/` directory.
- The `./data/` directory is created automatically on first run.

The container is configured with `restart: unless-stopped`, so it starts automatically after a server reboot.

---

## Web Server Reverse Proxy

> **How the production container works**: The Docker image is a multi-stage build that compiles the Vue frontend and embeds it inside the Django container as static files. This means a **single proxy rule to port 8000** serves everything from one domain:
>
> | Path | What it serves |
> |------|---------------|
> | `yourdomain.com/` | Vue SPA (frontend) |
> | `yourdomain.com/api/...` | REST API |
> | `yourdomain.com/admin` | Django admin panel |
>
> Port **5173** is the Vite development server — it only exists when running `docker-compose.dev.yml` locally and is not present in production.

The application listens on `127.0.0.1:8000` and is not directly accessible from the internet. Configure your web server to proxy all traffic to it.

### Apache2

Enable the required modules (if not already enabled):

```bash
sudo a2enmod proxy proxy_http
sudo systemctl reload apache2
```

**HTTP** — save as `/etc/apache2/sites-available/personal-crm.conf`:

```apache
<VirtualHost *:80>
    ServerName yourdomain.com

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

**HTTPS** (recommended — requires a TLS certificate, e.g. from Let's Encrypt):

```apache
<VirtualHost *:443>
    ServerName yourdomain.com

    SSLEngine on
    SSLCertificateFile /etc/letsencrypt/live/yourdomain.com/fullchain.pem
    SSLCertificateKeyFile /etc/letsencrypt/live/yourdomain.com/privkey.pem

    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>
```

Enable the site and reload:

```bash
sudo a2ensite personal-crm
sudo systemctl reload apache2
```

### Nginx

**HTTP** — save as `/etc/nginx/sites-available/personal-crm`:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**HTTPS**: Add `listen 443 ssl` with your certificate paths alongside the HTTP block (or use `certbot --nginx` to configure TLS automatically).

Enable the site and reload:

```bash
sudo ln -s /etc/nginx/sites-available/personal-crm /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

### CSRF Configuration for HTTPS

When the application is served over HTTPS, Django's CSRF protection requires the `CSRF_TRUSTED_ORIGINS` variable to match your public URL. Update your `.env` file:

```bash
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

Then restart the container to apply the change:

```bash
docker compose restart
```

Without this, you will see CSRF verification errors when submitting forms.

---

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `SECRET_KEY` | **Yes** | insecure dev key | Django cryptographic secret key. **Must be changed in production** — the default exposes your application to security attacks. Generate with: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `ALLOWED_HOSTS` | **Yes** | `localhost` | Comma-separated list of hostnames Django will serve. Must include your public domain in production (e.g. `yourdomain.com`). |
| `CSRF_TRUSTED_ORIGINS` | **Yes** | `http://localhost:8000` | Full URL(s) trusted for CSRF protection. Set to `https://yourdomain.com` when deployed with HTTPS — leaving this wrong will cause form submission errors. |
| `DATABASE_PATH` | No | `/app/data/db.sqlite3` | Path inside the container where the SQLite database is stored. The `./data` directory is mounted from the host, so the default is safe and recommended. |
| `DJANGO_SETTINGS_MODULE` | No | `crm.settings.production` | Django settings module. Do not change unless you know what you are doing. |
