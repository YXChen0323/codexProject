import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from utils import summarize_results


def test_summarize_results_empty():
    assert summarize_results([]) == "沒有任何資料。"


def test_summarize_results_basic():
    rows = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    summary = summarize_results(rows)
    assert "2" in summary
    assert "id" in summary and "name" in summary
