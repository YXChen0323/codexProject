import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from context_manager import ConversationContext


def test_record_and_history():
    ctx = ConversationContext(db_path=":memory:")
    ctx.record("alice", "hi", "hello")
    history = ctx.get_history("alice")
    assert len(history) == 2
    assert history[0].role == "user" and history[0].content == "hi"
    assert history[1].role == "assistant" and history[1].content == "hello"


def test_summary():
    ctx = ConversationContext(db_path=":memory:")
    for i in range(3):
        ctx.record("bob", f"q{i}", f"a{i}")
    summary = ctx.summarize("bob", max_chars=50)
    assert isinstance(summary, str)
    assert len(summary) <= 50


def test_reset():
    ctx = ConversationContext(db_path=":memory:")
    ctx.record("carol", "hi", "hello")
    ctx.reset("carol")
    history = ctx.get_history("carol")
    assert history == []
