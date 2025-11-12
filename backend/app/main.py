"""FastAPI entry-point for the site reporter backend."""

from fastapi import FastAPI

from .core.config import get_settings
from .routers.pipeline import router as workflow_router


def create_app() -> FastAPI:
    """Application factory used by uvicorn."""

    settings = get_settings()
    app = FastAPI(title=settings.project_name, version="0.1.0")

    @app.get("/health", tags=["health"])
    async def health_check() -> dict[str, str]:
        """Basic readiness probe."""

        return {"status": "ok", "service": settings.project_name}

    app.include_router(workflow_router)

    return app


app = create_app()

