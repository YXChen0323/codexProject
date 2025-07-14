"""Utility functions to manage prompt templates."""
from typing import Dict

# Nested mapping of model name to task to prompt template
PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "phi3:3.8b": {
        "sql": (
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Use only these columns exactly as provided: {columns}.\n"
            "Write an SQL query for the following question based solely on the column names and any prior conversation history: {query}\n"
            "Respond only with a valid SQL statement. Do not include any explanations or extra text."
        ),
        "chart": (
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Use only these columns exactly as provided: {columns}.\n"
            "Write an SQL query that lists multiple related data points for comparison in a chart based solely on the column names and any prior conversation history: {query}\n"
            "Respond only with a valid SQL statement. Do not include any explanations or extra text."
        ),
    },
    "qwen2.5-coder:7b": {
        "sql": (
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Use only these columns exactly as provided: {columns}.\n"
            "Write an SQL query for the following question based solely on the column names and any prior conversation history: {query}\n"
            "Respond only with a valid SQL statement. Do not include any explanations or extra text."
        ),
        "chart": (
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Use only these columns exactly as provided: {columns}.\n"
            "Write an SQL query that lists multiple related data points for comparison in a chart based solely on the column names and any prior conversation history: {query}\n"
            "Respond only with a valid SQL statement. Do not include any explanations or extra text."
        ),
        "nlp": (
            "Given the SQL query results:\n{results}\n"
            "Answer the question: {query} in a friendly and helpful way. Interpret the meaning of the results yourself and do not state that the meaning is unclear."
        ),
    },
    "qwen2.5-coder:3b": {
        "sql": (
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Use only these columns exactly as provided: {columns}.\n"
            "Write an SQL query for the following question based solely on the column names and any prior conversation history: {query}\n"
            "Respond only with a valid SQL statement. Do not include any explanations or extra text."
        ),
        "chart": (
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Use only these columns exactly as provided: {columns}.\n"
            "Write an SQL query that lists multiple related data points for comparison in a chart based solely on the column names and any prior conversation history: {query}\n"
            "Respond only with a valid SQL statement. Do not include any explanations or extra text."
        ),
        "nlp": (
            "Given the SQL query results:\n{results}\n"
            "Answer the question: {query} in a friendly and helpful way. Interpret the meaning of the results yourself and do not state that the meaning is unclear."
        ),
    },
    "sqlcoder:7b": {
        "sql": (
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Use only these columns exactly as provided: {columns}.\n"
            "Write an SQL query for the following question based solely on the column names and any prior conversation history: {query}\n"
            "Respond only with a valid SQL statement. Do not include any explanations or extra text."
        ),
        "chart": (
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Use only these columns exactly as provided: {columns}.\n"
            "Write an SQL query that lists multiple related data points for comparison in a chart based solely on the column names and any prior conversation history: {query}\n"
            "Respond only with a valid SQL statement. Do not include any explanations or extra text."
        ),
    },
    "llama3.2:3b": {
        "sql": (
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Use only these columns exactly as provided: {columns}.\n"
            "Write an SQL query for the following question based solely on the column names and any prior conversation history: {query}\n"
            "Respond only with a valid SQL statement. Do not include any explanations or extra text."
        ),
        "chart": (
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Use only these columns exactly as provided: {columns}.\n"
            "Write an SQL query that lists multiple related data points for comparison in a chart based solely on the column names and any prior conversation history: {query}\n"
            "Respond only with a valid SQL statement. Do not include any explanations or extra text."
        ),
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
    base_prompt = fill_template(template, query, results=results or "", **extra)
    if not history:
        return base_prompt
    history_text = "\n".join(f"{m.role}: {m.content}" for m in history)
    return f"{history_text}\n{base_prompt}"
