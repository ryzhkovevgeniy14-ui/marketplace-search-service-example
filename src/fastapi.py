from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.infrastructure.logging.config import configure_logging
from src.infrastructure.persistence.database import (
    create_engine,
    create_session_factory,
)
from src.presentation.api.dependencies import setup
from src.presentation.api.routes.public import router as public_router
from src.presentation.middleware.access_logging import AccessLoggingMiddleware
from src.presentation.middleware.tracing import TracingMiddleware
from src.settings import Settings


def create_app() -> FastAPI:
    configure_logging()

    settings = Settings()

    engine = create_engine(settings)
    session_factory = create_session_factory(engine)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        setup(settings, session_factory)
        yield

    app = FastAPI(title="Search Service", lifespan=lifespan)
    app.add_middleware(AccessLoggingMiddleware)
    app.add_middleware(TracingMiddleware)
    app.include_router(public_router)
    return app
