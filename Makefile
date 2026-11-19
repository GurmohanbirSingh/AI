SHELL := /bin/bash
COMPOSE := docker compose

.PHONY: help env dev down logs migrate seed-pilot test-api test-web lint typecheck verify smoke dry-run reset compose-config env-check

help:
	@echo "ShortsFactory AI — standard commands (blueprint Section 25)"
	@echo "  make dev          Start postgres, redis, api, worker and web"
	@echo "  make down         Stop services (volumes are preserved)"
	@echo "  make logs         Follow service logs"
	@echo "  make migrate      Apply database migrations (available from Phase 2)"
	@echo "  make seed-pilot   Seed the GTA 6 pilot channel (available from Phase 2)"
	@echo "  make test-api     Run Python tests in the API image"
	@echo "  make test-web     Run web unit tests in the web image"
	@echo "  make lint         Ruff + ESLint"
	@echo "  make typecheck    mypy + tsc --noEmit"
	@echo "  make verify       Everything a phase gate needs, including a live smoke test"
	@echo "  make dry-run      Confirm no-upload, no-paid-API safety defaults"
	@echo "  make reset        DESTRUCTIVE: stop and delete local volumes (asks first)"

env:
	@if [ ! -f .env ]; then cp .env.example .env; echo "Created .env from .env.example — change ADMIN_PASSWORD and SESSION_SECRET for anything beyond local dev."; else echo ".env already exists; leaving it untouched."; fi

dev: env
	$(COMPOSE) up -d --build
	@$(COMPOSE) ps

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f --tail=100

migrate:
	@if [ -f apps/api/alembic.ini ]; then \
		$(COMPOSE) run --rm api alembic upgrade head; \
	else \
		echo "No Alembic configuration yet. Database migrations are implemented in Phase 2."; \
	fi

seed-pilot:
	@if [ -d seeds ] && [ -f apps/api/app/workers/seed.py ]; then \
		$(COMPOSE) run --rm api python -m app.workers.seed; \
	else \
		echo "Pilot seed command is implemented in Phase 2 (seeds/ is created then)."; \
	fi

test-api: env
	$(COMPOSE) run --rm --no-deps api pytest

test-web: env
	$(COMPOSE) run --rm --no-deps web npm test

lint: env
	$(COMPOSE) run --rm --no-deps api sh -c "ruff check . && ruff format --check ."
	$(COMPOSE) run --rm --no-deps web npm run lint

typecheck: env
	$(COMPOSE) run --rm --no-deps api mypy app
	$(COMPOSE) run --rm --no-deps web npm run typecheck

compose-config: env
	$(COMPOSE) config -q
	@echo "docker compose config: OK"

env-check:
	python3 scripts/check_env_example.py

smoke: env
	bash scripts/smoke_phase1.sh

verify: env-check compose-config lint typecheck test-api test-web smoke
	@echo "Phase 1 verification completed."

dry-run: env
	python3 scripts/check_safety_defaults.py

reset:
	@read -r -p "This deletes local PostgreSQL/Redis volumes. Type 'delete-local-data' to continue: " answer; \
	if [ "$$answer" = "delete-local-data" ]; then \
		$(COMPOSE) down -v; \
	else \
		echo "Aborted; nothing was deleted."; \
	fi
