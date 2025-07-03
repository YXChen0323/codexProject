# MCP_119

This directory contains the `docker-compose.yaml` file that sets up the following services:

- **Ollama** - running in the `ollama/ollama` container.
- **pgAdmin** - graphical interface for PostgreSQL using `dpage/pgadmin4`.
- **PostgreSQL** - with PostGIS support using the `postgis/postgis:15-3.4` image.
- **FastAPI** - simple API server.
- **Nginx** - reverse proxy exposing the API under `/api/`.

The `fastapi` service connects to the PostgreSQL container using environment
variables defined in `docker-compose.yaml`. If you need to customise the
database credentials, update these variables accordingly.

The API container also communicates with the Ollama service. By default the
backend expects Ollama to be reachable at `http://localhost:11434`. When using
Docker Compose, the `OLLAMA_URL` environment variable is set so the backend
calls the `ollama` container instead.

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
