"""Utility helpers for the backend."""

import json

import answer_generator


def summarize_results(results: list[dict]) -> str:
    """Return a human friendly summary for query results."""
    if not results:
        return ""
    try:
        return answer_generator.generate_answer(
            "Summarize these query results in one sentence.", results
        )
    except Exception:
        columns = ", ".join(results[0].keys())
        return columns


def build_fallback_answer(question: str, results: list[dict]) -> str:
    """Return a natural language answer using an LLM as a fallback."""
    if not results:
        return ""
    try:
        return answer_generator.generate_answer(question, results)
    except Exception:
        columns = ", ".join(results[0].keys())
        return columns


