"""Utility functions to manage prompt templates."""

from typing import Dict

SQL_TEMPLATE = (
    "請根據下列資訊，僅產生最準確且完整的 SQL 查詢語句：\n"
    "1. 目標資料表：postgres.emergence.emergency_calls\n"
    "2. 可使用的欄位：{columns}\n"
    "3. 參考資料：{reference_info}\n"
    "4. 過往生成紀錄：{history}\n"
    "5. 使用者問題：{query}\n"
    "請注意：\n"
    "- 回答只能且必須是 SQL，不能包含任何解釋或其他內容。\n"
    "- 僅限列出前 20 筆資料，並以表格形式呈現。"
)


CHART_TEMPLATE = (
    "請根據下列資訊，僅產生可用於和其他資料對比的圖表 SQL 查詢語句：\n"
    "1. 目標資料表：postgres.emergence.emergency_calls\n"
    "2. 可使用的欄位：{columns}\n"
    "3. 參考資料：{reference_info}\n"
    "4. 既往生成紀錄：{history}\n"
    "5. 使用者問題：{query}\n"
    "請注意：\n"
    "- 查詢目的是讓使用者能和其他筆資料進行比較，產生對比圖表。\n"
    "- 回答只能且必須是 SQL，不能包含任何解釋或其他內容。"
)


# Nested mapping of model name to task to prompt template
NLP_TEMPLATE = (
    "請以友善且樂於助人的方式回答問題：{query}，並參照查詢結果：{results}。\n"
    "請自行解讀結果的意義，勿表示意義不明。\n"
    "以繁體中文回覆。"
)

PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "gpt-oss:latest": {
        "sql": SQL_TEMPLATE,
        "chart": CHART_TEMPLATE,
        "nlp": NLP_TEMPLATE,
    },
    "qwen2.5-coder:7b": {
        "sql": SQL_TEMPLATE,
        "chart": CHART_TEMPLATE,
        "nlp": NLP_TEMPLATE,
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
