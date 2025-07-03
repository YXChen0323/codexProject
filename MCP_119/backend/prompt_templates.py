"""Utility functions to manage prompt templates."""
from typing import Dict

# Nested mapping of model name to task to prompt template
PROMPT_TEMPLATES: Dict[str, Dict[str, str]] = {
    "phi3-3.8b": {
        "nlp": "Answer the following question: {query}",
    },
    "Qwen2.5-coder-7b": {
        "code": "Provide code to accomplish the task: {query}",
    },
    "sqlcoder-7b": {
        "sql": "Write an SQL query for: {query}",
    },
}


def load_template(model: str, task: str) -> str:
    """Return the prompt template for a given model and task."""
    return PROMPT_TEMPLATES.get(model, {}).get(task, "{query}")


def fill_template(template: str, query: str) -> str:
    """Insert the user's query into the template."""
    return template.format(query=query)
