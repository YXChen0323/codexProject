import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from urllib import request as urlrequest
import json
import answer_generator


class FakeResponse:
    def __init__(self, data: bytes):
        self.data = data

    def read(self):
        return self.data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


def test_generate_answer(monkeypatch):
    def fake_urlopen(req):
        return FakeResponse(json.dumps({"response": "hello"}).encode())

    monkeypatch.setattr(urlrequest, "urlopen", fake_urlopen)
    ans = answer_generator.generate_answer("q", [{"id": 1}])
    assert ans == "hello"
