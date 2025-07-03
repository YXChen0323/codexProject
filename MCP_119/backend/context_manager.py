from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from textwrap import shorten
from typing import List, Dict


@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ConversationContext:
    """In-memory conversation context manager."""

    def __init__(self) -> None:
        self._history: Dict[str, List[Message]] = defaultdict(list)

    def record(self, user_id: str, query: str, response: str) -> None:
        """Store a user query and assistant response."""
        self._history[user_id].append(Message("user", query))
        self._history[user_id].append(Message("assistant", response))

    def get_history(self, user_id: str) -> List[Message]:
        """Return the message history for a user."""
        return list(self._history.get(user_id, []))

    def summarize(self, user_id: str, max_chars: int = 200) -> str:
        """Return a simple summary of the conversation history."""
        messages = self._history.get(user_id, [])
        text = " ".join(f"{m.role}: {m.content}" for m in messages)
        return shorten(text, width=max_chars, placeholder="...")
