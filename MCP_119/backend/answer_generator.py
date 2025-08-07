import json
import os
from urllib import request as urlrequest
from dotenv import load_dotenv
import prompt_templates

load_dotenv(dotenv_path="../.env")

# OLLAMA_URL = os.getenv("OLLAMA_URL", "http://192.168.0.233:11434/api/generate")
OLLAMA_URL = os.getenv("OLLAMA_URL")

def generate_answer(question: str, results: list[dict], *, model: str = "llama3.2:3b") -> str:
    """Generate a friendly natural language answer using an LLM."""
    template = prompt_templates.load_template(model, "nlp")
    # 限制傳給 LLM 的資料量，預設只取前 20 筆
    limited_results = results[:20] if isinstance(results, list) else results
    results_text = json.dumps(limited_results, ensure_ascii=False)
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
