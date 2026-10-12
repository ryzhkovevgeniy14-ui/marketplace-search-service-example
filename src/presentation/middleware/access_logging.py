"""Access logging middleware с поддержкой распределённой трассировки."""

import logging
import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("access")


class AccessLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware для логирования HTTP запросов с trace_id.

    Логирует каждый запрос после обработки, включая trace_id из ContextVar.
    Должен быть установлен ПОСЛЕ TracingMiddleware, чтобы логирование
    происходило до reset_trace_id().

    Обрабатывает три сценария:
    - Успешный ответ (2xx, 3xx)
    - HTTP ошибка от handler или exception handler (4xx, 5xx)
    - Необработанное исключение (500, логируется до обработки Starlette)

    Логируемый status_code всегда соответствует фактическому HTTP ответу клиента.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()

        # Формирование client address заранее
        client_addr = "unknown"
        if request.client:
            client_addr = f"{request.client.host}:{request.client.port}"

        try:
            response = await call_next(request)

            # Логирование успешного ответа (до выхода из middleware)
            process_time_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info(
                '%s - "%s %s" %s %dms',
                client_addr,
                request.method,
                request.url.path,
                response.status_code,
                process_time_ms,
            )

            return response
        except Exception:
            # Логирование при исключении
            process_time_ms = int((time.perf_counter() - start_time) * 1000)
            logger.info(
                '%s - "%s %s" 500 %dms',
                client_addr,
                request.method,
                request.url.path,
                process_time_ms,
            )
            raise
