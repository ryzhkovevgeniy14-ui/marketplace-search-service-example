from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from src.infrastructure.tracing.context import get_trace_id
from src.presentation.middleware.tracing import TracingMiddleware


async def test_middleware_generates_trace_id_if_not_provided() -> None:
    app = FastAPI()
    app.add_middleware(TracingMiddleware)

    @app.get("/test")
    async def test_endpoint() -> dict[str, str | None]:
        return {"trace_id": get_trace_id()}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/test")
        assert resp.status_code == 200
        trace_id = resp.json()["trace_id"]
        assert trace_id is not None
        assert len(trace_id) == 36
        assert "X-Trace-Id" in resp.headers
        assert resp.headers["X-Trace-Id"] == trace_id


async def test_middleware_uses_provided_trace_id() -> None:
    app = FastAPI()
    app.add_middleware(TracingMiddleware)

    @app.get("/test")
    async def test_endpoint() -> dict[str, str | None]:
        return {"trace_id": get_trace_id()}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        custom_trace_id = "custom-trace-id-123"
        resp = await client.get("/test", headers={"X-Trace-Id": custom_trace_id})
        assert resp.status_code == 200
        assert resp.json()["trace_id"] == custom_trace_id
        assert resp.headers["X-Trace-Id"] == custom_trace_id


async def test_middleware_adds_trace_id_to_response_headers() -> None:
    app = FastAPI()
    app.add_middleware(TracingMiddleware)

    @app.get("/test")
    async def test_endpoint() -> dict[str, str]:
        return {"message": "ok"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/test")
        assert "X-Trace-Id" in resp.headers
        assert len(resp.headers["X-Trace-Id"]) == 36
