import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

import database


class FakeCursor:
    def __init__(self):
        self.description = [("id",), ("name",)]
        self.executed = None

    def execute(self, query):
        self.executed = query

    def fetchall(self):
        return [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConnection:
    def cursor(self, cursor_factory=None):
        return FakeCursor()

    def close(self):
        pass


class FakePsycopg:
    def connect(self, *args, **kwargs):
        return FakeConnection()


def test_execute_query(monkeypatch):
    monkeypatch.setattr(database, "psycopg2", FakePsycopg())
    result = database.execute_query("SELECT * FROM test")
    assert result == [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]
