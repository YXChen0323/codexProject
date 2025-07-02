# MCP_119

This directory contains the `docker-compose.yaml` file that sets up the following services:

- **Ollama** - running in the `ollama/ollama` container.
- **pgAdmin** - graphical interface for PostgreSQL using `dpage/pgadmin4`.
- **PostgreSQL** - with PostGIS support using the `postgis/postgis:15-3.4` image.
- **FastAPI** - simple API server.
- **Nginx** - reverse proxy exposing the API under `/api/`.

Start the stack:

```bash
docker compose up -d
```

Before running the stack for the first time, build the React application so Nginx can serve the static files:

```bash
(cd frontend/home && npm install && npm run build)
```

Stop the stack:

```bash
docker compose down
```
