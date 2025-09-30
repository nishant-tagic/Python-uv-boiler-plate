import time

from fastapi import APIRouter, Request

router = APIRouter(prefix="", tags=["health"])


@router.get("/ping")
async def health_check(request: Request):
    """health check endpoint"""
    return {
        "status": "Healthy Server",
        "timestamp": time.time(),
        "environment": getattr(request.app.state, "environment", "dev"),
        "request_id": getattr(request.state, "request_id", "unknown"),
        "version": getattr(request.app.state, "api_version", "1.0.0"),
    }
