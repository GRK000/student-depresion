-include .env
export

SHELL := /bin/bash

VENV := .venv
PYTHON := $(VENV)/bin/python
PYTEST := $(VENV)/bin/pytest
PIP := $(VENV)/bin/pip

PORT ?= 8000

.DEFAULT_GOAL := help

# ===================== INTERNAL HELPER =====================

$(VENV):
	@echo "ERROR: Virtual environment not found. Run 'make setup' first" && exit 1

# ===================== MANDATORY TARGETS =====================

help:
	@echo "Mandatory targets:"
	@echo "  make setup          — Create venv and install dependencies"
	@echo "  make test           — Run pytest tests"
	@echo "  make docker-build   — Build Docker image"
	@echo "  make docker-up      — Start the service"
	@echo "  make docker-down    — Stop the service"
	@echo "  make health         — Check service health"
	@echo "  make predict        — Make a sample prediction"
	@echo ""
	@echo "Optional targets:"
	@echo "  make dev            — Run API locally (uvicorn with hot-reload)"
	@echo "  make pipeline       — Run data pipeline"
	@echo "  make train          — Train model"
	@echo "  make clean          — Clean generated files"

setup:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "Setup complete. Activate with: source $(VENV)/bin/activate"

test: $(VENV)
	@test -d tests || (echo "ERROR: tests/ directory not found. Tests are added in Session 11." && exit 1)
	$(PYTEST) tests/ -v

docker-build:
	docker compose build

docker-up:
	mkdir -p data logs
	docker compose up -d
	@echo "Service started at http://localhost:$(PORT)"

docker-down:
	docker compose down

health:
	@set -o pipefail; curl -sf http://localhost:$(PORT)/health | python3 -m json.tool || \
		(echo "ERROR: Service not responding at /health" && exit 1)

predict:
	@set -o pipefail; curl -sf -X POST http://localhost:$(PORT)/predict \
		-H "Content-Type: application/json" \
		-d '{"age":28.0,"academic_pressure":3.0,"work_pressure":0.0,"cgpa":7.03,"study_satisfaction":5.0,"job_satisfaction":0.0,"work_study_hours":9.0,"financial_stress":1.0,"gender":"Male","sleep_duration":"Less than 5 hours","dietary_habits":"Healthy","degree":"BA","suicidal_thoughts":"No","family_history":"Yes"}' \
		| python3 -m json.tool || \
		(echo "ERROR: Prediction failed" && exit 1)

# ===================== OPTIONAL TARGETS =====================

dev: $(VENV)
	$(VENV)/bin/uvicorn app.api:app --reload --port 8000

pipeline: $(VENV)
	$(PYTHON) -m app.pipeline

train: $(VENV)
	$(PYTHON) -m app.train

clean:
	rm -rf $(VENV) .pytest_cache .mypy_cache
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -f data/*.parquet data/predictions.jsonl
	rm -f logs/*.log
	@echo "Cleaned"
