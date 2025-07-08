import json
import os
import re
from urllib import request as urlrequest

import database
import model_router
import prompt_templates


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

# When generating chart data the UI appends this suffix to the user's
# original question to request additional rows with the same columns and
# search the entire column to find the best station.
CHART_QUERY_SUFFIX = "加入更多相同欄位的資料，搜尋整個欄位找出最佳站點"


SQL_START = re.compile(r"^(SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|WITH)\b", re.IGNORECASE)


def _is_valid_sql(sql: str) -> bool:
    """Return True if the string appears to be a valid SQL statement."""
    return bool(SQL_START.match(sql))


CODE_FENCE_RE = re.compile(r"^```(?:sql)?\s*(.*?)\s*```$", re.IGNORECASE | re.DOTALL)


def _clean_sql(sql: str) -> str:
    """Remove markdown code fences from the generated SQL if present."""
    sql = sql.strip()
    match = CODE_FENCE_RE.match(sql)
    if match:
        sql = match.group(1).strip()
    return sql


def generate_sql(question: str, *, model: str | None = None) -> str:
    """Generate an SQL query from a natural language question using an LLM."""
    if model is None:
        model = model_router.ModelRouter().route(task_type="sql")

    template = prompt_templates.load_template(model, "sql")
    schema = database.describe_schema()
    samples = database.get_random_rows("emergency_calls", limit=3, schema="emergence")
    sample_text = "\n".join(str(row) for row in samples)
    columns = database.get_table_columns("emergency_calls", schema="emergence")
    columns_text = ", ".join(columns)
    prompt = prompt_templates.fill_template(
        template,
        question,
        schema=schema,
        samples=sample_text,
        columns=columns_text,
    )

    req = urlrequest.Request(
        OLLAMA_URL,
        data=json.dumps({"model": model, "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req) as resp:
        text = resp.read().decode()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        # The response may contain multiple JSON objects without a
        # surrounding array. Decode them sequentially and merge the
        # "response" fields to reconstruct the full SQL string.
        decoder = json.JSONDecoder()
        remaining = text
        chunks: list[str] = []
        last_obj: dict | None = None
        while remaining.strip():
            try:
                obj, idx = decoder.raw_decode(remaining.lstrip())
            except json.JSONDecodeError:
                break
            chunks.append(str(obj.get("response", "")))
            last_obj = obj
            remaining = remaining.lstrip()[idx:]

        if last_obj is None:
            raise
        last_obj["response"] = "".join(chunks)
        data = last_obj
    sql = _clean_sql(data.get("response", ""))
    if not _is_valid_sql(sql):
        raise ValueError(f"Generated text is not valid SQL: {sql}")
    return sql


def generate_chart_sql(question: str, *, model: str | None = None) -> str:
    """Generate SQL for chart data based on the user's question."""
    chart_question = f"{question}，{CHART_QUERY_SUFFIX}"
    return generate_sql(chart_question, model=model)
