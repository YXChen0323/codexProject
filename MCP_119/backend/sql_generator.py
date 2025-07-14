import json
import os
import re
from urllib import request as urlrequest

import model_router
import prompt_templates
import database


OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")


def _llm_enabled() -> bool:
    """Return True if SQL generation via LLM is enabled."""
    flag = os.getenv("ENABLE_LLM_SQL", "true").lower()
    return flag not in {"0", "false", "no"}



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


def generate_sql(
    question: str,
    *,
    model: str | None = None,
    history: list | None = None,
) -> str:
    """Generate an SQL query from a natural language question using an LLM."""
    if not _llm_enabled():
        raise RuntimeError("LLM SQL generation is disabled")
    if model is None:
        model = model_router.ModelRouter().route(task_type="sql")

    columns = database.get_table_columns("emergency_calls", schema="emergence")
    columns_text = ", ".join(columns)
    prompt = prompt_templates.build_prompt_with_history(
        model,
        "sql",
        question,
        history or [],
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


def generate_chart_sql(
    question: str,
    *,
    model: str | None = None,
    history: list | None = None,
) -> str:
    """Generate an SQL query for chart comparison using an LLM."""
    if not _llm_enabled():
        raise RuntimeError("LLM SQL generation is disabled")
    if model is None:
        model = model_router.ModelRouter().route(task_type="sql")

    columns = database.get_table_columns("emergency_calls", schema="emergence")
    columns_text = ", ".join(columns)
    prompt = prompt_templates.build_prompt_with_history(
        model,
        "chart",
        question,
        history or [],
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


