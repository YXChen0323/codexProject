import json
import os
from urllib import request as urlrequest

import prompt_templates

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://host.docker.internal:11434/api/generate")


def generate_answer(question: str, results: list[dict], *, model: str = "llama3.2:3b") -> str:
    """Generate a friendly natural language answer using an LLM."""
    template = prompt_templates.load_template(model, "nlp")
    results_text = json.dumps(results, ensure_ascii=False)
    prompt = prompt_templates.fill_template(template, question, results=results_text)
    req = urlrequest.Request(
        OLLAMA_URL,
        data=json.dumps({"model": model, "prompt": prompt, "stream": False}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlrequest.urlopen(req) as resp:
        text = resp.read().decode()
    data = json.loads(text)
    return data.get("response", "").strip()
