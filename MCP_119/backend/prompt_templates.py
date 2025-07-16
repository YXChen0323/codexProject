"""Utility functions to manage prompt templates."""

from typing import Dict

SQL_TEMPLATE = (
    "-- 目標資料表：postgres.emergence.emergency_calls\n"
    "-- 可使用的欄位：{columns}\n"
    "-- 參考資料：{reference_info}\n"
    "-- 既往生成紀錄：{history}\n"
    "-- 使用者問題：{query}\n"
    "請根據上述資訊輸出完整 SQL 語句，僅回傳 SQL。"
)

CHART_TEMPLATE = (
    "-- 目標資料表：postgres.emergence.emergency_calls\n"
    "-- 可使用的欄位：{columns}\n"
    "-- 參考資料：{reference_info}\n"
    "-- 既往生成紀錄：{history}\n"
    "-- 使用者問題：{query}\n"
    "請根據上述資訊輸出可採用於圖表比較的 SQL 語句，擷取相同欄位的其他筆資料作為比較對象，僅回傳 SQL。"
)

# Nested mapping of model name to task to prompt template
PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "phi3:3.8b": {"sql": SQL_TEMPLATE, "chart": CHART_TEMPLATE},
    "qwen2.5-coder:7b": {
        "sql": SQL_TEMPLATE,
        "chart": CHART_TEMPLATE,
        "nlp": (
            "Given the SQL query results:\n{results}\n"
            "請以友善且樂於助人的方式回答問題：{query}。請自行解讀結果的意義，勿表示意義不明。"
        ),
    },
    "qwen2.5-coder:3b": {
        "sql": SQL_TEMPLATE,
        "chart": CHART_TEMPLATE,
        "nlp": (
            "Given the SQL query results:\n{results}\n"
            "請以友善且樂於助人的方式回答問題：{query}。請自行解讀結果的意義，勿表示意義不明。"
        ),
    },
    "sqlcoder:7b": {"sql": SQL_TEMPLATE, "chart": CHART_TEMPLATE},
    "llama3.2:3b": {
        "sql": SQL_TEMPLATE,
        "chart": CHART_TEMPLATE,
        "nlp": (
            "Given the SQL query results:\n{results}\n"
            "請以友善且樂於助人的方式回答問題：{query}。請自行解讀結果的意義，勿表示意義不明。"
        ),
    },
}


def load_template(model: str, task: str) -> str:
    """Return the prompt template for a given model and task."""
    return PROMPT_TEMPLATES.get(model, {}).get(task, "{query}")


def fill_template(template: str, query: str, **extra: str) -> str:
    """Insert the user's query and any extra data into the template."""
    return template.format(query=query, **extra)


def build_prompt_with_history(
    model: str,
    task: str,
    query: str,
    history: list,
    results: str | None = None,
    **extra: str,
) -> str:
    """Return a prompt that includes conversation history and optional data."""
    template = load_template(model, task)
    history_text = (
        "\n".join(f"{m.role}: {m.content}" for m in history) if history else ""
    )
    base_prompt = fill_template(
        template,
        query,
        history=history_text,
        results=results or "",
        **extra,
    )
    if "{history}" in template or not history_text:
        return base_prompt
    return f"{history_text}\n{base_prompt}"
