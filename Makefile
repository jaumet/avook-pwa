.PHONY: dev test format seed

DEV_COMPOSE=infra/docker-compose.yml

## Start the local development environment
dev:
@echo "Starting Audiovook stack via docker compose..."
docker compose -f $(DEV_COMPOSE) up --build

## Run the API test suite
test:
@echo "Running placeholder tests (to be expanded)."
docker compose -f $(DEV_COMPOSE) exec -T api pytest -q || echo "Tests not yet implemented"

## Auto-format code and fix lint issues
format:
@echo "Running formatters (placeholder)."
docker compose -f $(DEV_COMPOSE) exec -T api ruff check --fix . || echo "Formatters not yet configured"

## Seed the database with initial development data
seed:
@echo "Seeding database (placeholder)."
docker compose -f $(DEV_COMPOSE) exec -T api python -m app.scripts.seed || echo "Seed script pending"
