# Multi-stage build for ML API service

# ==================== BASE STAGE ====================
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies (separate layer for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user with standard UID 1000
RUN useradd -m -u 1000 appuser && \
    mkdir -p data logs && \
    chown -R appuser:appuser /app

# ==================== PRODUCTION STAGE ====================
FROM base AS production

# Copy application code
# --chown is required because COPY always runs as root, regardless of any USER instruction.
# Without it, the copied files would be owned by root even though appuser owns /app.
COPY --chown=appuser:appuser app/ ./app/
COPY --chown=appuser:appuser models/ ./models/
COPY --chown=appuser:appuser config/ ./config/

# Switch to non-root user
USER appuser

# Container always uses port 8000 internally
EXPOSE 8000

# Health check (internal port is always 8000)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]