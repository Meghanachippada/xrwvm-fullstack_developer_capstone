# -------- Stage 1: build the React frontend --------
FROM node:18-alpine AS frontend
WORKDIR /frontend
COPY server/frontend/package*.json ./
RUN npm ci
COPY server/frontend/ ./
RUN npm run build

# -------- Stage 2: Python/Django app --------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY server/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY server/manage.py ./manage.py
COPY server/djangoproj ./djangoproj
COPY server/djangoapp  ./djangoapp

# include the React build inside the image
COPY --from=frontend /frontend/build ./frontend/build

COPY server/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# keep your lowercase envs (your code expects these)
ENV backend_url="http://dealership:3000" \
    sentiment_analyzer_url="http://sentiment:5050/"

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn","--bind",":8000","--workers","3","djangoproj.wsgi"]
