import os
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except Exception:  # pragma: no cover - optional dependency may be missing
    psycopg2 = None
    RealDictCursor = None


def _get_connection():
    if psycopg2 is None:
        raise ImportError("psycopg2 is required to use execute_query")
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "mydb"),
        user=os.getenv("DB_USER", "user"),
        password=os.getenv("DB_PASSWORD", "123456"),
    )


def execute_query(query: str) -> list[dict]:
    """Execute an SQL query and return the results as a list of dicts."""
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(query)
            rows = cur.fetchall()
            return [dict(row) for row in rows]
    finally:
        conn.close()
