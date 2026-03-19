"""
Main FastAPI application entry point.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from src.config.settings import settings
from src.api.routers import health, hello
from src.utils.logging import configure_logging

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting Kanban Backend API")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Kanban Backend API")


# Create FastAPI application
app = FastAPI(
    title="Kanban Backend API",
    description="Backend API for the Kanban project management application",
    version="0.1.0",
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url="/api/redoc" if settings.environment != "production" else None,
    openapi_url="/api/openapi.json" if settings.environment != "production" else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (for frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for uncaught exceptions.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_server_error",
        },
    )


# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(hello.router, prefix="/api/hello", tags=["hello"])


@app.get("/")
async def root():
    """
    Root endpoint that serves a simple welcome message.
    """
    return {
        "message": "Welcome to Kanban Backend API",
        "version": "0.1.0",
        "docs": "/api/docs" if settings.environment != "production" else None,
    }


@app.get("/api")
async def api_root():
    """
    API root endpoint.
    """
    return {
        "message": "Kanban Backend API",
        "endpoints": {
            "health": "/api/health",
            "hello": "/api/hello",
            "docs": "/api/docs",
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )