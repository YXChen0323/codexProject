"""Utility helpers for the backend."""


def summarize_results(results: list[dict]) -> str:
    """Return a short human friendly summary for query results."""
    if not results:
        return "沒有任何資料。"
    row_count = len(results)
    columns = ", ".join(results[0].keys())
    return f"共 {row_count} 筆資料，欄位包含 {columns}。"
