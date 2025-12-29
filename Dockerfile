FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Install dependencies
RUN pip install --no-cache-dir     flask     requests     prometheus-client     apscheduler     pytz     gunicorn

# Copy application files
COPY app.py collector.py database.py config.py templates.py ./

# Create data directory
RUN mkdir -p /app/data

# Security: run as non-root (create app user)
RUN useradd -m -u 1000 appuser &&     chown -R appuser:appuser /app
USER appuser

EXPOSE 8095

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=30s     CMD curl -f http://localhost:8095/health || exit 1

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:8095", "--workers", "2", "--timeout", "60", "--access-logfile", "-", "app:app"]
