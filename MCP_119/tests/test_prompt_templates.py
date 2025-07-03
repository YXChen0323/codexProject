import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from prompt_templates import load_template, fill_template


def test_load_template():
    template = load_template("phi3-3.8b", "nlp")
    assert template == "Answer the following question: {query}"


def test_fill_template():
    template = "Hello {query}"
    result = fill_template(template, "world")
    assert result == "Hello world"
