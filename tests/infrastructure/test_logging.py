import logging

from src.infrastructure.logging.config import configure_logging
from src.infrastructure.tracing.context import reset_trace_id, set_trace_id


class RecordCapture(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


def test_log_record_contains_trace_id() -> None:
    configure_logging()
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    handler = RecordCapture()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    trace_id = "test-trace-789"
    token = set_trace_id(trace_id)
    try:
        logger.info("test message")
        assert len(handler.records) == 1
        record = handler.records[0]
        assert hasattr(record, "trace_id")
        assert record.trace_id == trace_id
    finally:
        reset_trace_id(token)
        logger.removeHandler(handler)


def test_log_record_handles_missing_trace_id() -> None:
    configure_logging()
    logger = logging.getLogger("test_logger_no_trace")
    logger.setLevel(logging.INFO)
    handler = RecordCapture()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("test message")
    assert len(handler.records) == 1
    record = handler.records[0]
    assert hasattr(record, "trace_id")
    assert record.trace_id == "no-trace"
    logger.removeHandler(handler)
