.PHONY: setup dev migrate test lint typecheck build test-integration test-e2e benchmark backup restore

setup:
	pip install -e services/api
	cd apps/web && npm install

dev-api:
	cd services/api && uvicorn app.main:app --reload --port 8000

dev-web:
	cd apps/web && npm run dev

dev:
	docker compose up

migrate:
	alembic upgrade head

test:
	python -m pytest services/api/tests -v

lint:
	python -m flake8 services/api --ignore=E501,W503 || true

typecheck:
	cd apps/web && npm run typecheck

build:
	cd apps/web && npm run build

test-integration:
	python -m pytest services/api/tests/integration -v

test-e2e:
	python -m pytest tests/e2e -v

benchmark:
	python scripts/benchmark.py

backup:
	python scripts/backup_db.py

restore:
	python scripts/restore_db.py
