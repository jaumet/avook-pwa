# avook-pwa

## Local Development

To start the local development environment, run the following command from the root of the repository:

```bash
docker compose -f infra/docker-compose.yml up
```

This will start all the necessary services:
- **PWA (Frontend):** http://localhost:5173
- **API (Backend):** http://localhost:8000
- **Stream Proxy (NGINX):** http://localhost:8080
- **Local S3 (LocalStack):** http://localhost:9000
