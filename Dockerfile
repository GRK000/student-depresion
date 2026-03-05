FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (curl needed for HEALTHCHECK)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (separate layer for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and assets
COPY app/ ./app/
COPY models/ ./models/
COPY config/ ./config/

# Internal port (always 8000 inside the container)
EXPOSE 8000

# Health check — uses the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Start the API (bind to 0.0.0.0 so the port is accessible from outside the container)
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
