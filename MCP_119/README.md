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

Start the stack:

```bash
docker compose up -d
```

Before running the stack for the first time, build the React application so Nginx can serve the static files. The UI now uses a modern style defined in `src/App.css`:

```bash
(cd frontend/home && npm install && npm run build)
```

The frontend also visualizes query results using a simple bar chart when numeric data is available.
When preparing the chart, the UI sends a second query by appending
"加入更多相同欄位的資料，搜尋整個欄位找出最佳站點" to the user's original
question. This instructs the LLM to return more rows with the same columns
and also search across the entire column so the chart can show data from
additional records (for example other fire stations) while the main answer
and table remain based on the original question.
The additional SQL used to fetch data for the chart is now shown below the
main query results so you can inspect or reuse it if needed.
You can also generate this follow-up query directly using the
`generate_chart_sql()` helper in `backend/sql_generator.py`.

Stop the stack:

```bash
docker compose down
```
