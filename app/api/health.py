import time

from fastapi import APIRouter, Request

from app.core.logging import get_logger

router = APIRouter(prefix="", tags=["health"])


@router.get("/ping")
async def health_check(request: Request):
    
    logger = get_logger(__name__)
    """health check endpoint"""
    logger.info("Health check endpoint called")
    time.sleep(2.1)  # Simulate some processing delay
    return {
        "status": "Healthy Server",
        "timestamp": time.time(),
        "environment": getattr(request.app.state, "environment", "dev"),
        "request_id": getattr(request.state, "request_id", "unknown"),
        "version": getattr(request.app.state, "api_version", "1.0.0"),
    }
