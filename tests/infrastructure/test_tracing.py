from src.infrastructure.tracing.context import (
    generate_trace_id,
    get_trace_id,
    reset_trace_id,
    set_trace_id,
)


def test_set_and_get_trace_id() -> None:
    trace_id = "test-trace-123"
    token = set_trace_id(trace_id)
    try:
        assert get_trace_id() == trace_id
    finally:
        reset_trace_id(token)


def test_reset_trace_id() -> None:
    initial_value = get_trace_id()
    trace_id = "test-trace-456"
    token = set_trace_id(trace_id)
    assert get_trace_id() == trace_id
    reset_trace_id(token)
    assert get_trace_id() == initial_value


def test_generate_trace_id() -> None:
    trace_id = generate_trace_id()
    assert isinstance(trace_id, str)
    assert len(trace_id) == 36
    parts = trace_id.split("-")
    assert len(parts) == 5
