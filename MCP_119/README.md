# MCP_119

This directory contains the `docker-compose.yaml` file that sets up the following services:

- **Ollama** - running in the `ollama/ollama` container.
- **pgAdmin** - graphical interface for PostgreSQL using `dpage/pgadmin4`.
- **PostgreSQL** - with PostGIS support using the `postgis/postgis:15-3.4` image.
- **FastAPI** - simple API server.
- **Nginx** - reverse proxy exposing the API under `/api/`.
  All backend endpoints return JSON-RPC 2.0 formatted responses.

The `fastapi` service connects to the PostgreSQL container using environment
variables defined in `docker-compose.yaml`. If you need to customise the
database credentials, update these variables accordingly.

The API container also communicates with the Ollama service. By default the
backend expects Ollama to be reachable at `http://localhost:11434`. When using
Docker Compose, the `OLLAMA_URL` environment variable is set so the backend
calls the `ollama` container instead. The backend disables streaming when
requesting a response from Ollama so a complete JSON payload is returned.

Set `ENABLE_LLM_SQL=true` in the backend environment (enabled by default) to
allow the API to call the language model for SQL generation. Set it to `false`
if you want to disable this feature.

Query summaries and fallback answers are produced using the same LLM to
provide human-friendly explanations when possible.

The `ollama` service is configured to run with GPU acceleration. It sets
`NVIDIA_VISIBLE_DEVICES=all` and requires the NVIDIA container runtime. You
can verify GPU access with:

```bash
docker compose exec ollama nvidia-smi
```

Start the stack:

```bash
docker compose up -d
```

Before running the stack for the first time, build the React application so Nginx can serve the static files. The UI now uses a modern style defined in `src/App.css`:

```bash
(cd frontend/home && npm install && npm run build)

The frontend now includes a simple chart view powered by `chart.js` and
`react-chartjs-2`. A checkbox lets you choose whether to generate a chart.
When unchecked, the UI only generates SQL from your question without
executing it. Enable the checkbox if you want chart data returned and
visualised as a bar chart when possible.
```


Stop the stack:

```bash
docker compose down
```

## Natural language answers

When you execute a query through the `/sql/execute` endpoint (or via the UI),
the backend automatically runs the `nlp` prompt template with the LLM. This
generates a friendly natural language explanation of the results that is
returned in the `answer` field and displayed in the frontend. If no question is
provided, the results are summarised with the same model to produce a brief
description. If the `answer` is empty, the UI falls back to a short summary of
the data.
The prompt was adjusted to remove the required follow-up question so answers
sound more natural.
