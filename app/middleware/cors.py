from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)

def setup_cors(app: FastAPI, config: Settings) -> None:
    """Setup CORS with environment-aware configuration"""

    if config.ENVIRONMENT.lower() == "local":
        allowed_origins = ["*"]  # Allow all origins in development
        allow_credentials = True
        allow_methods = ["*"]
        allow_headers = ["*"]
        logger.info("CORS set for local environment: allow all origins")
    else:
        allowed_origins = config.CORS_ORIGINS
        allow_credentials = False
        allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
        allow_headers = [
            "Content-Type",
            "Authorization",
            "X-Request-ID",
            "X-API-Key"
        ]
        logger.info(f"CORS allowed origins: {allowed_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=allow_methods,
        allow_headers=allow_headers,
        expose_headers=[
            "X-Request-ID",
            "X-Process-Time"
        ],
    )
