# Stage 1: Build React frontend
FROM node:25-alpine AS frontend-builder

WORKDIR /frontend

# Copy package files and install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim

WORKDIR /app

ARG APP_VERSION=dev
ARG APP_REVISION=unknown
ARG APP_BUILD_DATE=
ENV APP_VERSION=$APP_VERSION \
    APP_REVISION=$APP_REVISION \
    APP_BUILD_DATE=$APP_BUILD_DATE

# Install curl for healthcheck and build dependencies for cffi
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Remove build dependencies to reduce image size
RUN apt-get update && apt-get remove -y gcc && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY app.py wsgi.py locks.py collector.py database.py config.py car_utils.py public_api.py time_utils.py http_client.py ./

# Copy built React frontend from Stage 1
COPY --from=frontend-builder /frontend/dist ./static

# Create data directory
RUN mkdir -p /app/data

# Security: run as non-root (create app user)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8095

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=30s \
    CMD curl -f http://localhost:8095/health || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8095", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "wsgi:app"]
