from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import SecurityConfig, Environment
from app.core.logging import get_logger

logger = get_logger(__name__)

def setup_cors(app: FastAPI, config: SecurityConfig) -> None:
    """Setup CORS with environment-aware configuration"""
    
    allowed_origins = config.cors_origins
    logger.info(f"CORS allowed origins: {allowed_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=[
            "Content-Type", 
            "Authorization", 
            "X-Request-ID",
            "X-API-Key"
        ],
        expose_headers=[
            "X-Request-ID", 
            "X-Process-Time", 
            "X-RateLimit-Remaining"
        ],
    )
