# MCP_119

This directory contains the `docker-compose.yaml` file that sets up the following services:

- **Ollama** - running in the `ollama/ollama` container.
- **pgAdmin** - graphical interface for PostgreSQL using `dpage/pgadmin4`.
- **PostgreSQL** - with PostGIS support using the `postgis/postgis:15-3.4` image.

Start the stack:

```bash
docker compose up -d
```

Stop the stack:

```bash
docker compose down
```
