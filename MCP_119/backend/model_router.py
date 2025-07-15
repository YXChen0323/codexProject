from typing import Dict, Optional


class ModelRouter:
    """Simple router that selects a model based on user or task type."""

    def __init__(self) -> None:
        # Mapping of task types to model names
        self.task_mapping: Dict[str, str] = {
            # qwen2.5-coder:7b handles user facing responses
            "sql": "qwen2.5-coder:7b",
            # qwen2.5-coder:3b is a lightweight variant for simple NLP tasks
            "nlp-small": "qwen2.5-coder:3b",
            # All three models generate SQL queries
            "code": "phi3:3.8b",
            "sql": "sqlcoder:7b",
            # llama3.2:3b is available for general NLP tasks
            "chat": "llama3.2:3b",
        }
        # Optional mapping of user IDs to preferred model names
        self.user_mapping: Dict[str, str] = {}

    def add_user_preference(self, user_id: str, model_name: str) -> None:
        """Record a preferred model for a specific user."""
        self.user_mapping[user_id] = model_name

    def route(self, *, task_type: Optional[str] = None, user_id: Optional[str] = None) -> str:
        """Return the model name based on provided information."""
        if user_id and user_id in self.user_mapping:
            return self.user_mapping[user_id]
        if task_type and task_type in self.task_mapping:
            return self.task_mapping[task_type]
        # Default model if nothing matches
        return self.task_mapping["nlp"]

    def list_models(self) -> list[str]:
        """Return a list of all known model names."""
        models = set(self.task_mapping.values()) | set(self.user_mapping.values())
        return sorted(models)
