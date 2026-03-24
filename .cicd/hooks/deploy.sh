#!/bin/bash
set -e

echo "=== Phase 3: Deploy ==="
cp .env.production .env
make docker-down 2>/dev/null || true
make docker-build
make docker-up
echo "=== Deploy completed ==="
