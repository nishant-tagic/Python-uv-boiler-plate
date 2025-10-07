from contextvars import ContextVar
from typing import Optional

# Context variable to store request ID across async calls
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    """Get the current request ID from context."""
    return request_id_var.get()


def set_request_id(request_id: str) -> None:
    """Set the request ID in context."""
    request_id_var.set(request_id)
