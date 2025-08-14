# ---------- Stage 1: build React frontend ----------
FROM node:18-alpine AS frontend
WORKDIR /frontend
COPY server/frontend/package*.json ./
RUN npm ci
COPY server/frontend/ ./
RUN npm run build

# ---------- Stage 2: Python/Django app ----------
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Minimal OS deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Python deps
COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Django project files
COPY server/manage.py ./manage.py
COPY server/djangoproj ./djangoproj
COPY server/djangoapp  ./djangoapp

# Bring in the built React app
COPY --from=frontend /frontend/build ./frontend/build

# Default envs (you can override at docker run / in K8s)
ENV backend_url="http://database:3000" \
    sentiment_analyzer_url="http://sentiment:5050/"

EXPOSE 8000
CMD bash -lc "python manage.py migrate && python manage.py runserver 0.0.0.0:8000"
