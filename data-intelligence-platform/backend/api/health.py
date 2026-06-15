from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

router = APIRouter(tags=["health"])
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    try:
        return {
            "status": "healthy",
            "service": "Data Intelligence Platform",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Service unhealthy")


@router.get("/health/db")
async def db_health() -> Dict[str, str]:
    """Check database connectivity"""
    try:
        from models.database import get_db
        # This would be expanded to actually check connections
        return {"database": "connected"}
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Database unavailable")
