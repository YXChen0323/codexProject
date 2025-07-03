import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import database


class FakeCursor:
    def __init__(self, rows=None):
        self.description = [("id",), ("name",)]
        self.executed = None
        self.rows = rows or [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]

    def execute(self, query):
        self.executed = query

    def fetchall(self):
        return self.rows

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def __init__(self, rows=None):
        self.rows = rows

    def cursor(self, cursor_factory=None):
        return FakeCursor(self.rows)

    def close(self):
        pass


class FakePsycopg:
    def __init__(self, rows=None):
        self.rows = rows

    def connect(self, *args, **kwargs):
        return FakeConnection(self.rows)


def test_execute_query(monkeypatch):
    monkeypatch.setattr(database, "psycopg2", FakePsycopg())
    result = database.execute_query("SELECT * FROM test")
    assert result == [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]


def test_describe_schema(monkeypatch):
    rows = [
        {"table_name": "users", "column_name": "id"},
        {"table_name": "users", "column_name": "name"},
        {"table_name": "orders", "column_name": "id"},
        {"table_name": "orders", "column_name": "amount"},
    ]
    monkeypatch.setattr(database, "psycopg2", FakePsycopg(rows))
    schema = database.describe_schema()
    assert "users(id, name)" in schema
    assert "orders(id, amount)" in schema
