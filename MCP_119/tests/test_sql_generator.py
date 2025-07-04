import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from urllib import request as urlrequest
import json
import sql_generator
import pytest
import database


class FakeResponse:
    def __init__(self, data: bytes):
        self.data = data

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


def test_generate_sql(monkeypatch):
    def fake_urlopen(req):
        return FakeResponse(json.dumps({"response": "SELECT 1;"}).encode())

    monkeypatch.setattr(urlrequest, "urlopen", fake_urlopen)
    monkeypatch.setattr(database, "describe_schema", lambda: "tbl(col)")
    monkeypatch.setattr(database, "get_random_rows", lambda *a, **k: [{"id": 1}])
    monkeypatch.setattr(database, "get_table_columns", lambda *a, **k: ["id"]) 
    sql = sql_generator.generate_sql("test question")
    assert sql == "SELECT 1;"


def test_generate_sql_invalid(monkeypatch):
    def fake_urlopen(req):
        return FakeResponse(json.dumps({"response": "列出前五筆資料"}).encode())

    monkeypatch.setattr(urlrequest, "urlopen", fake_urlopen)
    monkeypatch.setattr(database, "describe_schema", lambda: "tbl(col)")
    monkeypatch.setattr(database, "get_random_rows", lambda *a, **k: [{"id": 1}])
    monkeypatch.setattr(database, "get_table_columns", lambda *a, **k: ["id"]) 
    with pytest.raises(ValueError):
        sql_generator.generate_sql("bad question")


def test_generate_sql_streaming(monkeypatch):
    data = "\n".join([
        json.dumps({"response": "SELECT ", "done": False}),
        json.dumps({"response": "1;", "done": True}),
    ])

    def fake_urlopen(req):
        return FakeResponse(data.encode())

    monkeypatch.setattr(urlrequest, "urlopen", fake_urlopen)
    monkeypatch.setattr(database, "describe_schema", lambda: "tbl(col)")
    monkeypatch.setattr(database, "get_random_rows", lambda *a, **k: [{"id": 1}])
    monkeypatch.setattr(database, "get_table_columns", lambda *a, **k: ["id"]) 
    sql = sql_generator.generate_sql("question")
    assert sql == "SELECT 1;"


def test_generate_sql_codeblock(monkeypatch):
    def fake_urlopen(req):
        return FakeResponse(json.dumps({"response": "```sql\nSELECT 1;\n```"}).encode())

    monkeypatch.setattr(urlrequest, "urlopen", fake_urlopen)
    monkeypatch.setattr(database, "describe_schema", lambda: "tbl(col)")
    monkeypatch.setattr(database, "get_random_rows", lambda *a, **k: [{"id": 1}])
    monkeypatch.setattr(database, "get_table_columns", lambda *a, **k: ["id"]) 
    sql = sql_generator.generate_sql("question")
    assert sql == "SELECT 1;"
