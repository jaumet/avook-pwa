# Audiovook — Access Manager & Player

Audiovook is a mono-repository that hosts both the FastAPI backend and the SvelteKit
progressive web app for the player experience. This iteration focuses on bootstrapping
the infrastructure needed to run the stack locally with Docker.

## Prerequisites

- Docker & Docker Compose
- Make
- Node.js 20+ (only required when running the web app directly on the host)

## Getting Started

1. Duplicate `.env.example` and name it `.env`. Adjust any values you require for your
   local environment. If you skip this step, the stack will still boot using the default
   development values baked into the services, and you can add the file later when you
   need to override secrets or connection details.
2. Build and start the development stack:

   ```bash
   make dev
   ```

   The command spins up the following services:

   - **api** — FastAPI application exposed on `http://localhost:8000`
   - **web** — SvelteKit dev server exposed on `http://localhost:5173`
   - **db** — PostgreSQL 15 with persisted storage
   - **cache** — Redis 7 for caching/rate-limiting needs
   - **nginx** — Reverse proxy available on `http://localhost:8080`

3. Visit `http://localhost:8080` to confirm Nginx is proxying the SvelteKit interface.
   The FastAPI health check is available at `http://localhost:8000/health`.

## Useful Commands

```bash
make dev      # build and start the full stack
make stop     # stop all containers
make logs     # tail service logs
make test     # run API tests inside the api container
make migrate  # apply Alembic migrations to the database
make format   # apply Ruff, Black and Prettier formatting
make seed     # execute the placeholder database seed script
```

All commands operate through Docker Compose, so you do not need to install Python or
Node dependencies locally. Run `make migrate` once the containers are up to create the
database schema and sample QR codes required for development.

## Directory Overview

```
avook.pwa/
  apps/
    api/            # FastAPI service
    web/            # SvelteKit progressive web app
  infra/            # Docker, reverse proxy, deployment assets
  .github/          # CI/CD workflows
```

Both applications currently expose minimal placeholder features but share the final
project layout so that subsequent work can focus on business logic and UI.
