#!/bin/bash
set -e

echo "=== Phase 2: Quality Gates ==="

# Load only METADATA_PATH if not already set
if [ -z "$METADATA_PATH" ] && [ -f .env ]; then
    METADATA_PATH=$(grep -E '^METADATA_PATH=' .env | head -n1 | cut -d= -f2-)
fi

if [ -z "$METADATA_PATH" ] || [ ! -f "$METADATA_PATH" ]; then
    echo "ERROR: Metadata file not found: ${METADATA_PATH:-<not set>}"
    exit 1
fi

version=$(jq -r '.version' "$METADATA_PATH")
ready=$(jq -r '.deployment_ready' "$METADATA_PATH")
f1=$(jq -r '.metrics.f1_score' "$METADATA_PATH")
echo "Model $version: f1=$f1, deployment_ready=$ready"

if [ "$ready" != "true" ]; then
    echo "ERROR: Model not ready for deployment"
    exit 1
fi

echo "=== Pre-deploy checks passed ==="
