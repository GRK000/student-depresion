#!/bin/bash
set -e

echo "=== Phase 4: Smoke Tests ==="

echo "Waiting for service to start..."
MAX_RETRIES=6
for i in $(seq 1 $MAX_RETRIES); do
    if make health 2>/dev/null; then
        echo "Health check passed (attempt $i)"
        break
    fi
    if [ "$i" -eq "$MAX_RETRIES" ]; then
        echo "ERROR: Service not healthy after $MAX_RETRIES attempts"
        exit 1
    fi
    echo "Retry $i/$MAX_RETRIES in 5s..."
    sleep 5
done

make predict

echo "=== Post-deploy checks passed ==="
