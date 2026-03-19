"""
API router modules.
"""
from src.api.routers.health import router as health_router
from src.api.routers.hello import router as hello_router

__all__ = [
    "health",
    "hello",
]