from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from textwrap import shorten
from typing import List
import sqlite3


@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ConversationContext:
    """SQLite-backed conversation context manager."""

    def __init__(self, db_path: str = "conversation.db") -> None:
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_table()

    def _create_table(self) -> None:
        with self._conn:
            self._conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp TEXT
                )
                """
            )

    def record(self, user_id: str, query: str, response: str) -> None:
        """Store a user query and assistant response."""
        with self._conn:
            self._conn.execute(
                "INSERT INTO messages (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, "user", query, datetime.utcnow().isoformat()),
            )
            self._conn.execute(
                "INSERT INTO messages (user_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, "assistant", response, datetime.utcnow().isoformat()),
            )

    def get_history(self, user_id: str) -> List[Message]:
        """Return the message history for a user."""
        cur = self._conn.execute(
            "SELECT role, content, timestamp FROM messages WHERE user_id=? ORDER BY id",
            (user_id,),
        )
        rows = cur.fetchall()
        return [
            Message(row["role"], row["content"], datetime.fromisoformat(row["timestamp"]))
            for row in rows
        ]

    def summarize(self, user_id: str, max_chars: int = 200) -> str:
        """Return a simple summary of the conversation history."""
        messages = self.get_history(user_id)
        text = " ".join(f"{m.role}: {m.content}" for m in messages)
        return shorten(text, width=max_chars, placeholder="...")

    def reset(self, user_id: str) -> None:
        """Clear all stored messages for the given user."""
        with self._conn:
            self._conn.execute(
                "DELETE FROM messages WHERE user_id=?",
                (user_id,),
            )

    def close(self) -> None:
        self._conn.close()
