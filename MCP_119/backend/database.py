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
        dbname=os.getenv("DB_NAME", "postgres"),
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


def describe_schema() -> str:
    """Return a simple text description of tables and columns in the database."""
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT table_name, column_name
                FROM information_schema.columns
                WHERE table_schema = 'postgres'
                ORDER BY table_name, ordinal_position
                """
            )
            rows = cur.fetchall()
    finally:
        conn.close()

    tables: dict[str, list[str]] = {}
    for row in rows:
        tables.setdefault(row["table_name"], []).append(row["column_name"])
    return "; ".join(
        f"{tbl}({', '.join(cols)})" for tbl, cols in tables.items()
    )



def get_table_columns(table: str, *, schema: str | None = None) -> list[str]:
    """Return a list of column names for the specified table."""
    conn = _get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            schema_clause = f"table_schema = '{schema}'" if schema else "table_schema = 'postgres'"
            query = (
                "SELECT column_name FROM information_schema.columns "
                f"WHERE {schema_clause} AND table_name = '{table}' ORDER BY ordinal_position"
            )
            cur.execute(query)
            rows = cur.fetchall()
            return [row["column_name"] for row in rows]
    finally:
        conn.close()
