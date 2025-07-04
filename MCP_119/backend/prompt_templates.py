"""Utility functions to manage prompt templates."""
from typing import Dict

# Nested mapping of model name to task to prompt template
PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "phi3:3.8b": {
        "sql": (
            "Given the database schema:\n{schema}\n"
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Always use `FROM emergence.emergency_calls` in the SQL.\n"
            "Table columns include: {columns}\n"
            "You must generate the SQL based strictly on the provided columns (do not modify them) and the question.\n"
            "Here are 3 randomly sampled records for reference:\n{samples}\n"
            "Write an SQL query for: {query}\n"
            "Respond only with a valid SQL statement and filter out any non-SQL text."
        ),
    },
    "qwen2.5-coder:7b": {
        "sql": (
            "Given the database schema:\n{schema}\n"
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Always use `FROM emergence.emergency_calls` in the SQL.\n"
            "Table columns include: {columns}\n"
            "You must generate the SQL based strictly on the provided columns (do not modify them) and the question.\n"
            "Here are 3 randomly sampled records for reference:\n{samples}\n"
            "Write an SQL query for: {query}\n"
            "Respond only with a valid SQL statement and filter out any non-SQL text."
        ),
        "nlp": (
            "Given the SQL query results:\n{results}\n"
            "Answer the question: {query} in a friendly and helpful way."
        ),
    },
    "sqlcoder:7b": {
        "sql": (
            "Given the database schema:\n{schema}\n"
            "The table to query is `emergency_calls` in the `emergence` schema.\n"
            "Always use `FROM emergence.emergency_calls` in the SQL.\n"
            "Table columns include: {columns}\n"
            "You must generate the SQL based strictly on the provided columns (do not modify them) and the question.\n"
            "Here are 3 randomly sampled records for reference:\n{samples}\n"
            "Write an SQL query for: {query}\n"
            "Respond only with a valid SQL statement and filter out any non-SQL text."
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
    model: str, task: str, query: str, history: list, results: str | None = None
) -> str:
    """Return a prompt that includes conversation history and optional query results."""
    template = load_template(model, task)
    base_prompt = fill_template(template, query, results=results or "")
    if not history:
        return base_prompt
    history_text = "\n".join(f"{m.role}: {m.content}" for m in history)
    return f"{history_text}\n{base_prompt}"
