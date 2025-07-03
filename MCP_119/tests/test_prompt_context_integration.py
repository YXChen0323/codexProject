import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from prompt_templates import build_prompt_with_history
from context_manager import ConversationContext


def test_build_prompt_with_history():
    ctx = ConversationContext(db_path=":memory:")
    ctx.record("alice", "hi", "hello")
    ctx.record("alice", "how are you", "fine")
    history = ctx.get_history("alice")
    prompt = build_prompt_with_history("Qwen2.5-coder-7b", "nlp", "what's up?", history)
    assert "user: hi" in prompt
    assert "assistant: hello" in prompt
    assert "what's up?" in prompt
