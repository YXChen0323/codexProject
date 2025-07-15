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

### Initialize the frontend (first time only)
Install React and add Tailwind CSS dependencies:

```bash
npx create-react-app home
cd home
npm install -D tailwindcss@3.4.17 postcss autoprefixer
npx tailwindcss init -p
npm install -D @tailwindcss/forms @tailwindcss/typography
npm install -D daisyui
npm install recharts
```

### Build the React app
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

## Prepare the database

Copy the example CSV file into the PostGIS container and load it:

```bash
docker cp Fire_Department_and_Emergency_Medical_Services_Dispatched_Calls_for_Service_20250512.csv postgis:/home
```

```sql
CREATE SCHEMA IF NOT EXISTS emergence;

CREATE TABLE emergence.emergency_calls (
    "call_number" TEXT,
    "unit_id" TEXT,
    "incident_number" TEXT,
    "call_type" TEXT,
    "call_date" DATE,
    "watch_date" DATE,
    "received_dttm" TIMESTAMP,
    "entry_dttm" TIMESTAMP,
    "dispatch_dttm" TIMESTAMP,
    "response_dttm" TIMESTAMP,
    "on_scene_dttm" TIMESTAMP,
    "transport_dttm" TIMESTAMP,
    "hospital_dttm" TIMESTAMP,
    "call_final_disposition" TEXT,
    "available_dttm" TIMESTAMP,
    "address" TEXT,
    "city" TEXT,
    "zipcode_of_incident" TEXT,
    "battalion" TEXT,
    "station_area" TEXT,
    "box" TEXT,
    "original_priority" TEXT,
    "priority" TEXT,
    "final_priority" TEXT,
    "als_unit" TEXT,
    "call_type_group" TEXT,
    "number_of_alarms" INT,
    "unit_type" TEXT,
    "unit_sequence_in_call_dispatch" TEXT,
    "fire_prevention_district" TEXT,
    "supervisor_district" TEXT,
    "neighborhooods_-_analysis_boundaries" TEXT,
    "rowid" TEXT,
    "case_location" TEXT,
    "data_as_of" DATE,
    "data_loaded_at" TIMESTAMP,
    "analysis_neighborhoods" TEXT
);

COPY emergence.emergency_calls FROM '/home/Fire_Department_and_Emergency_Medical_Services_Dispatched_Calls_for_Service_20250512.csv' WITH (FORMAT csv, HEADER true);
```

## UI features

The frontend includes a chart view powered by `chart.js` and `react-chartjs-2`.
A checkbox lets you choose whether to generate and display a bar chart.

## Natural language answers

Queries sent to `/sql/execute` trigger the `nlp` prompt template so the LLM can
produce a human-friendly explanation of the results. When no question is
provided, a short summary is generated instead. Answers no longer force a
follow-up question, resulting in more natural responses.
