"""FastAPI bootstrap for the Site Reporter backend."""

from fastapi import FastAPI

from .api import api_router
from .core.config import get_settings


def create_app() -> FastAPI:
    """Spin up the FastAPI app with config and routers."""

    settings = get_settings()
    app = FastAPI(title=settings.project_name, version="0.1.0")

    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Handy readiness probe for uptime checks."""

        return {"status": "ok", "service": settings.project_name}

    app.include_router(api_router)

    return app


app = create_app()
