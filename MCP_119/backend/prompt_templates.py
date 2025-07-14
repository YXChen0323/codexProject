"""Utility functions to manage prompt templates."""

from typing import Dict

SQL_TEMPLATE = (
    "-- \u76ee\u6a19\u8cc7\u6599\u8868\uff1aemergence.emergency_calls\n"
    "-- \u53ef\u4f7f\u7528\u7684\u6b04\u4f4d\uff1a{columns}\n"
    "-- \u53c3\u8003\u8cc7\u6599\uff1a{reference_info}\n"
    "-- \u65e2\u5f80\u751f\u6210\u7d00\u9304\uff1a{history}\n"
    "-- \u4f7f\u7528\u8005\u554f\u984c\uff1a{query}\n"
    "\u8acb\u6839\u64da\u4e0a\u8ff0\u8cc7\u8a0a\u8f38\u51fa\u5b8c\u6574 SQL \u8a9e\u53e5\uff0c\u50c5\u56de\u50b3 SQL\u3002"
)

CHART_TEMPLATE = (
    "-- \u76ee\u6a19\u8cc7\u6599\u8868\uff1aemergence.emergency_calls\n"
    "-- \u53ef\u4f7f\u7528\u7684\u6b04\u4f4d\uff1a{columns}\n"
    "-- \u53c3\u8003\u8cc7\u6599\uff1a{reference_info}\n"
    "-- \u65e2\u5f80\u751f\u6210\u7d00\u9304\uff1a{history}\n"
    "-- \u4f7f\u7528\u8005\u554f\u984c\uff1a{query}\n"
    "\u8acb\u6839\u64da\u4e0a\u8ff0\u8cc7\u8a0a\u8f38\u51fa\u53ef\u63a1\u7528\u65bc\u5716\u8868\u6bd4\u8f03\u7684 SQL \u8a9e\u53e5\uff0c\u50c5\u56de\u50b3 SQL\u3002"
)

# Nested mapping of model name to task to prompt template
PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "phi3:3.8b": {"sql": SQL_TEMPLATE, "chart": CHART_TEMPLATE},
    "qwen2.5-coder:7b": {
        "sql": SQL_TEMPLATE,
        "chart": CHART_TEMPLATE,
        "nlp": (
            "Given the SQL query results:\n{results}\n"
            "Answer the question: {query} in a friendly and helpful way. Interpret the meaning of the results yourself and do not state that the meaning is unclear."
        ),
    },
    "qwen2.5-coder:3b": {
        "sql": SQL_TEMPLATE,
        "chart": CHART_TEMPLATE,
        "nlp": (
            "Given the SQL query results:\n{results}\n"
            "Answer the question: {query} in a friendly and helpful way. Interpret the meaning of the results yourself and do not state that the meaning is unclear."
        ),
    },
    "sqlcoder:7b": {"sql": SQL_TEMPLATE, "chart": CHART_TEMPLATE},
    "llama3.2:3b": {
        "sql": SQL_TEMPLATE,
        "chart": CHART_TEMPLATE,
        "nlp": (
            "Given the SQL query results:\n{results}\n"
            "Answer the question: {query} in a friendly and helpful way. Interpret the meaning of the results yourself and do not state that the meaning is unclear."
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
