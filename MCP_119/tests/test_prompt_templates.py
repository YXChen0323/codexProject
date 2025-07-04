import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from prompt_templates import load_template, fill_template


def test_load_template():
    template_big = load_template("qwen2.5-coder:7b", "nlp")
    template_small = load_template("qwen2.5-coder:3b", "nlp")
    assert "SQL query results" in template_big
    assert "SQL query results" in template_small


def test_fill_template():
    template = "Hello {query}"
    result = fill_template(template, "world")
    assert result == "Hello world"
