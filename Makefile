.PHONY: dev stop logs test format seed

DEV_COMPOSE=infra/docker-compose.yml
COMPOSE=docker compose -f $(DEV_COMPOSE)

## Start the local development environment
dev:
	$(COMPOSE) up --build

## Stop and remove containers
stop:
	$(COMPOSE) down

## Tail logs from running services
logs:
	$(COMPOSE) logs -f

## Run the API test suite
test:
	$(COMPOSE) run --rm api pytest -q

## Auto-format code and fix lint issues
format:
	$(COMPOSE) run --rm api ruff check --fix app
	$(COMPOSE) run --rm api black app
	$(COMPOSE) run --rm web npm run format

## Seed the database with initial development data
seed:
	$(COMPOSE) run --rm api python -m app.scripts.seed
