# MCP_119

`docker-compose.yaml` 用來協調開發環境，包含 PostGIS 資料庫、FastAPI 後端以及支援語言模型的 React 前端。也整合 pgAdmin 方便管理，並由 Nginx 提供 UI。

## 服務

- **Ollama** — `ollama/ollama`
- **pgAdmin** — `dpage/pgadmin4`
- **PostgreSQL** 搭配 PostGIS — `postgis/postgis:15-3.4`
- **FastAPI** 後端（JSON-RPC）
- **Nginx** 反向代理，對外暴露 `/api/`

後端容器使用 `docker-compose.yaml` 中設定的環境變數以連線 PostgreSQL 並取得 Ollama 服務。若需自訂帳號或端點，可調整該設定。設定 `ENABLE_LLM_SQL=true`（預設）即可讓語言模型產生 SQL；如不需要，可將其關閉。查詢摘要與備援回答亦由同一模型產生。

Ollama 容器使用 GPU 加速執行（`NVIDIA_VISIBLE_DEVICES=all`）。可以以下指令確認 GPU 是否可用：

```bash
docker compose exec ollama nvidia-smi
```

## 安裝步驟

### 首次初始化前端
安裝 React 並加入 Tailwind CSS 相關套件：

```bash
npx create-react-app home
cd home
npm install -D tailwindcss@3.4.17 postcss autoprefixer
npx tailwindcss init -p
npm install -D @tailwindcss/forms @tailwindcss/typography
npm install -D daisyui
npm install recharts
```

### 建立 React 應用
在啟動整個開發環境前，先建立 React 應用，讓 Nginx 能供應靜態檔案：

```bash
(cd frontend/home && npm install && npm run build)
```

 接著啟動所有服務：

```bash
docker compose up -d
```

 若要停止容器，可執行：

```bash
docker compose down
```

## 準備資料庫

將範例 CSV 檔從本機複製至 PostGIS 容器並匯入：

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

## 介面功能

前端內建由 `chart.js` 與 `react-chartjs-2` 驅動的圖表檢視，可通過勾選框決定是否產生並顯示長條圖。

## 自然語言回覆

當透過 `/sql/execute` 送出查詢時，將啟用 `nlp` 提示模板，使語言模型產生容易讀懂的結果說明。如果沒有提供問題，將產生簡短摘要。回答不再強制包含後續問題，使回覆更加自然。
