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
    "- 查詢結果僅需列出前100筆資料。"
)


CHART_TEMPLATE = (
    "請根據下列資訊，僅產生可用於和其他資料對比的圖表 SQL 查詢語句：\n"
    "1. 目標資料表：postgres.emergence.emergency_calls\n"
    "2. 可使用的欄位：{columns}\n"
    "3. 參考資料：{reference_info}\n"
    "4. 既往生成紀錄：{history}\n"
    "5. 使用者問題：{query}\n"
    "請注意：\n"
    "- 查詢目的是讓使用者能和同一欄位下不同類型、分類、值的資料進行比較，產生對比圖表。\n"
    "- 請根據問題語意，適當選擇分組欄位與聚合方式（如 group by、count、sum、avg 等），y 軸應為資料量、次數或統計結果。\n"
    "- 若適用，可同時查詢多個類型或分類的資料。\n"
    "- 查詢結果僅需列出前100筆資料。\n"
    "- 回答只能且必須是 SQL，不能包含任何解釋或其他內容。"
)


# Nested mapping of model name to task to prompt template
NLP_TEMPLATE = (
    "請根據使用者的提問：{query}，以及下列 SQL 查詢結果，給出精簡且人性化的繁體中文說明：\n{results}\n"
    "回應需結合提問與查詢資料的意義，並以易懂、友善的方式摘要重點，不需重複列出原始資料。"
)

PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "gpt-oss:20b": {
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
    """Insert the user's query and any extra data into the template. 若 results 為 list 且過大，僅取前 20 筆。"""
    # 處理 results 欄位，避免資料過大
    results = extra.get('results', None)
    if isinstance(results, list) and len(results) > 20:
        import json
        extra['results'] = json.dumps(results[:20], ensure_ascii=False)
    elif isinstance(results, list):
        import json
        extra['results'] = json.dumps(results, ensure_ascii=False)
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
