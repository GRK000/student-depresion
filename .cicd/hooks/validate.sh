#!/bin/bash
set -e

echo "=== Phase 1: Validation ==="
cp .env.production .env
make docker-test
echo "=== Validation passed ==="
