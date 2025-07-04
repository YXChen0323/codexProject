import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))
from model_router import ModelRouter


def test_list_models():
    router = ModelRouter()
    router.add_user_preference("alice", "custom-model")
    models = router.list_models()
    assert set(models) == {
        "phi3:3.8b",
        "qwen2.5-coder:7b",
        "qwen2.5-coder:3b",
        "sqlcoder:7b",
        "llama3.2:3b",
        "custom-model",
    }

