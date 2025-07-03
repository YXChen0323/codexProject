import json
from urllib import request as urlrequest
import prompt_templates
import model_router


OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_sql(question: str, *, model: str | None = None) -> str:
    """Generate an SQL query from a natural language question using an LLM."""
    if model is None:
        model = model_router.ModelRouter().route(task_type="sql")

    template = prompt_templates.load_template(model, "sql")
    prompt = prompt_templates.fill_template(template, question)

    req = urlrequest.Request(
        OLLAMA_URL,
        data=json.dumps({"model": model, "prompt": prompt}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req) as resp:
        data = json.load(resp)
    sql = data.get("response", "")
    return sql.strip()
