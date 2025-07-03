"""Utility functions for JSON-RPC 2.0 message creation."""
from typing import Any, Dict, Optional
from uuid import uuid4

JSON_RPC_VERSION = "2.0"

def build_request(method: str, params: Optional[Dict[str, Any]] | None = None, id: Optional[str] | None = None) -> Dict[str, Any]:
    """Create a JSON-RPC request object."""
    if id is None:
        id = str(uuid4())
    return {
        "jsonrpc": JSON_RPC_VERSION,
        "method": method,
        "params": params or {},
        "id": id,
    }


def build_response(result: Any | None = None, id: Optional[str] | None = None, error: Optional[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    """Create a JSON-RPC response object with either result or error."""
    response = {
        "jsonrpc": JSON_RPC_VERSION,
        "id": id,
    }
    if error is not None:
        response["error"] = error
    else:
        response["result"] = result
    return response
