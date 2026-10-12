import uuid
from contextvars import ContextVar, Token
from typing import Optional

_trace_id_context: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)


def get_trace_id() -> Optional[str]:
    return _trace_id_context.get()


def set_trace_id(trace_id: str) -> Token[Optional[str]]:
    return _trace_id_context.set(trace_id)


def reset_trace_id(token: Token[Optional[str]]) -> None:
    _trace_id_context.reset(token)


def generate_trace_id() -> str:
    return str(uuid.uuid4())
