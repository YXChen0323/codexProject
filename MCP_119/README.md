# MCP_119

`docker-compose.yaml` orchestrates a development stack that combines a PostGIS
database, a FastAPI backend and a React frontend with language‑model support.
pgAdmin is included for administration and Nginx serves the UI.

## Services

- **Ollama** — `ollama/ollama`
- **pgAdmin** — `dpage/pgadmin4`
- **PostgreSQL** with PostGIS — `postgis/postgis:15-3.4`
- **FastAPI** backend (JSON‑RPC)
- **Nginx** reverse proxy exposing `/api/`

Backend containers use the environment variables defined in
`docker-compose.yaml` to connect to PostgreSQL and reach the Ollama service.
Adjust them if you require custom credentials or endpoints. Set
`ENABLE_LLM_SQL=true` (default) to allow SQL generation by the language model or
disable it to skip that step. Query summaries and fallback answers are produced
by the same LLM.

The Ollama container runs with GPU acceleration (`NVIDIA_VISIBLE_DEVICES=all`).
Verify GPU access with:

```bash
docker compose exec ollama nvidia-smi
```

## Setup

Before starting the stack, build the React application so Nginx can serve the
static files:

```bash
(cd frontend/home && npm install && npm run build)
```

Start all services with:

```bash
docker compose up -d
```

Stop the containers using:

```bash
docker compose down
```

## UI features

The frontend includes a chart view powered by `chart.js` and `react-chartjs-2`.
A checkbox lets you choose whether to generate and display a bar chart. You can
also click **Map** after a query to plot any returned GeoJSON or latitude and
longitude columns on an interactive Leaflet map.

## Natural language answers

Queries sent to `/sql/execute` trigger the `nlp` prompt template so the LLM can
produce a human-friendly explanation of the results. When no question is
provided, a short summary is generated instead. Answers no longer force a
follow-up question, resulting in more natural responses.
