"""
API router modules.
"""
from src.api.routers.health import router as health_router
from src.api.routers.hello import router as hello_router
from src.api.routers.boards import router as boards_router
from src.api.routers.columns import router as columns_router
from src.api.routers.cards import router as cards_router

__all__ = [
    "health",
    "hello",
    "boards",
    "columns",
    "cards",
]