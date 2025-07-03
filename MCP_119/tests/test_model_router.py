import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from model_router import ModelRouter


def test_task_type_routing():
    router = ModelRouter()
    assert router.route(task_type="code") == "Qwen2.5-coder-7b"


def test_user_preference_routing():
    router = ModelRouter()
    router.add_user_preference("alice", "custom-model")
    assert router.route(user_id="alice") == "custom-model"
