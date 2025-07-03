"""Utility functions to manage prompt templates."""
from typing import Dict

# Nested mapping of model name to task to prompt template
PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    # All models now share the same SQL template
    "phi3:3.8b": {
        "sql": (
            "Given the database schema:\n{schema}\n"
            "Write an SQL query for: {query}"
        ),
    },
    "qwen2.5-coder:7b": {
        # Used for SQL generation and human friendly responses
        "sql": (
            "Given the database schema:\n{schema}\n"
            "Write an SQL query for: {query}"
        ),
        "nlp": "Answer the following question: {query}",
    },
    "sqlcoder:7b": {
        "sql": (
            "Given the database schema:\n{schema}\n"
            "Write an SQL query for: {query}"
        ),
    },
}


def load_template(model: str, task: str) -> str:
    """Return the prompt template for a given model and task."""
    return PROMPT_TEMPLATES.get(model, {}).get(task, "{query}")


def fill_template(template: str, query: str, **extra: str) -> str:
    """Insert the user's query and any extra data into the template."""
    return template.format(query=query, **extra)


def build_prompt_with_history(model: str, task: str, query: str, history: list) -> str:
    """Return a prompt that includes conversation history followed by the user's query."""
    template = load_template(model, task)
    base_prompt = fill_template(template, query)
    if not history:
        return base_prompt
    history_text = "\n".join(f"{m.role}: {m.content}" for m in history)
    return f"{history_text}\n{base_prompt}"
