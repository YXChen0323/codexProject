import os, requests, json
import psycopg2
from psycopg2.extras import execute_values

API = "https://data.sfgov.org/resource/nuek-vuh3.json"
APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN", "")
PG_DSN = os.getenv("PG_DSN")
TABLE = "emergence.emergency_calls"
PKS   = ["call_number", "unit_id"]   # 主鍵/唯一鍵欄位

# --------- DB Schema 偵測 ---------
def load_schema(conn, table=TABLE):
    schema, tbl = table.split(".")
    with conn.cursor() as cur:
        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema=%s AND table_name=%s
            ORDER BY ordinal_position
        """, (schema, tbl))
        return [r[0] for r in cur.fetchall()]

def make_upsert_sql(cols, pks=PKS):
    insert_cols = ",".join(cols)
    updates = ",".join([f"{c}=EXCLUDED.{c}" for c in cols if c not in pks])
    return f"""
    INSERT INTO {TABLE} ({insert_cols})
    VALUES %s
    ON CONFLICT ({",".join(pks)}) DO UPDATE SET
    {updates};
    """

# --------- API 拉資料 ---------
def fetch_batch(since=None, limit=1000, offset=0):
    params = {
      "$limit": limit,
      "$offset": offset,
      "$order": "data_loaded_at ASC"
    }
    if since:
        params["$where"] = f"data_loaded_at > '{since}'"
    headers = {"X-App-Token": APP_TOKEN} if APP_TOKEN else {}
    r = requests.get(API, params=params, headers=headers, timeout=60)
    r.raise_for_status()
    return r.json()

# --------- 清洗 ---------
def clean_value(v):
    if v is None:
        return None
    if isinstance(v, str):
        v = v.strip()
        if v == "":
            return None
        return v
    if isinstance(v, (dict, list)):     # dict / list → JSON string
        return json.dumps(v, ensure_ascii=False)
    return v

def clean_record(rec, cols):
    rec = {k.lower().replace(" ", "_"): clean_value(v) for k,v in rec.items()}
    return [clean_value(rec.get(c)) for c in cols]

# --------- Main ---------
def main():
    with psycopg2.connect(PG_DSN) as conn:
        cols = load_schema(conn, TABLE)
        UPSERT_SQL = make_upsert_sql(cols, PKS)

        # 找出 DB 已有的最新 data_loaded_at
        with conn.cursor() as cur:
            cur.execute(f"SELECT coalesce(max(data_loaded_at), '2000-01-01') FROM {TABLE};")
            last_ts = cur.fetchone()[0].isoformat()

        print(f"[INFO] Last timestamp in DB = {last_ts}")

        offset = 0
        total_upserts = 0
        while True:
            batch = fetch_batch(since=last_ts, limit=1000, offset=offset)
            if not batch:
                break

            rows = [clean_record(x, cols) for x in batch]
            with conn.cursor() as cur:
                execute_values(cur, UPSERT_SQL, rows, page_size=500)

            total_upserts += len(rows)
            offset += len(batch)
            print(f"[INFO] Upserted {len(rows)} rows (offset={offset})")

        print(f"[INFO] Total upserted rows = {total_upserts}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}")
        raise
