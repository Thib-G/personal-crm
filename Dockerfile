# Stage 1: Build Vue frontend
FROM node:22-alpine AS vue-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci --silent
COPY frontend/ .
RUN npm run build

# Stage 2: Django runtime
FROM python:3.13-slim
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Django project
COPY backend/ .

# Copy built Vue assets into Django static root
COPY --from=vue-builder /frontend/dist ./staticfiles/spa

# Run collectstatic
RUN DJANGO_SETTINGS_MODULE=crm.settings.production \
    SECRET_KEY=collectstatic-placeholder \
    ALLOWED_HOSTS=localhost \
    DATABASE_PATH=/tmp/collectstatic.sqlite3 \
    python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "crm.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "2", \
     "--threads", "2", \
     "--worker-class", "sync", \
     "--timeout", "30", \
     "--access-logfile", "-"]
