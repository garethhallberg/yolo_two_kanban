"""
Health check endpoints for monitoring and readiness.
"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.config.database import get_db
from src.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/")
async def health_check():
    """
    Basic health check endpoint.
    
    Returns:
        dict: Health status and timestamp
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "kanban-backend",
    }


@router.get("/live")
async def liveness_probe():
    """
    Liveness probe for Kubernetes/container orchestration.
    
    Returns:
        dict: Liveness status
    """
    return {"status": "alive"}


@router.get("/ready")
async def readiness_probe(db: Session = Depends(get_db)):
    """
    Readiness probe that checks database connectivity.
    
    Args:
        db: Database session dependency
        
    Returns:
        dict: Readiness status with database connectivity
    """
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        db_connected = False
    
    return {
        "status": "ready" if db_connected else "not_ready",
        "database": "connected" if db_connected else "disconnected",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/version")
async def version_info():
    """
    Get application version information.
    
    Returns:
        dict: Version details
    """
    return {
        "name": "kanban-backend",
        "version": "0.1.0",
        "description": "FastAPI backend for Kanban project management",
        "environment": "development",
    }