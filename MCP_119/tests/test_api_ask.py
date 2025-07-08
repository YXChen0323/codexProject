import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
import main


def test_ask(monkeypatch):
    app = main.app

    monkeypatch.setattr(main.sql_generator, "generate_sql", lambda q, model=None: "SELECT 1;")
    monkeypatch.setattr(main.database, "execute_query", lambda q: [{"count": 1}])
    monkeypatch.setattr(main.answer_generator, "generate_answer", lambda q, r, model=None: "hi")

    client = TestClient(app)
    resp = client.post("/api/ask", json={"question": "q"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"]["sql"] == "SELECT 1;"
    assert data["result"]["results"] == [{"count": 1}]
    assert data["result"]["answer"] == "hi"
