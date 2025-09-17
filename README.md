# Audiovook — Access Manager & Player

This repository contains the mono-repo for the Audiovook PWA experience. It is intentionally
minimal at this stage and focuses on providing the agreed project structure so that subsequent
features can be layered in incrementally.

## Repository Layout

```
avook.pwa/
  apps/
    api/            # FastAPI service
    web/            # SvelteKit progressive web app
  infra/            # Docker, reverse proxy, deployment assets
  .github/          # CI/CD workflows
```

Each directory already includes placeholder modules and configuration files that will be extended
in future tasks.

## Getting Started

1. Duplicate `.env.example` into `.env` and customise as required.
2. Use the provided `Makefile` targets to interact with the stack. The commands currently emit
   placeholder messages until the full Docker environment and scripts are implemented.

```
make dev
make test
make format
make seed
```

A detailed setup guide will be added alongside the infrastructure implementation work.
