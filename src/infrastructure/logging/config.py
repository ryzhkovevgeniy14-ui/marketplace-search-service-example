import logging
from typing import Any

from src.infrastructure.tracing.context import get_trace_id

_original_factory = logging.getLogRecordFactory()


def _trace_id_log_record_factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
    record = _original_factory(*args, **kwargs)
    trace_id = get_trace_id()
    record.trace_id = trace_id if trace_id else "no-trace"
    return record


def configure_logging() -> None:
    logging.setLogRecordFactory(_trace_id_log_record_factory)
    log_format = (
        "%(asctime)s [%(levelname)s] [trace_id=%(trace_id)s] %(name)s: %(message)s"
    )
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
