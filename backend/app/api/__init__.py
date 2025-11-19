"""API package exposing the versioned router."""

from fastapi import APIRouter

from .routes import workflow

api_router = APIRouter(prefix="/api")
api_router.include_router(workflow.router)

__all__ = ["api_router"]
