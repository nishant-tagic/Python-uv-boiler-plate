import time
import uuid
from typing import Callable, Dict

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger, log_request, log_slow_request
from app.config.config import Settings

logger = get_logger(__name__)
settings = Settings()  # Load settings once


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Handles security headers, request logging, slow requests, and request IDs.
    """

    def __init__(self, app):
        super().__init__(app)

        # Pull configuration from Settings
        self.api_version = settings.APP_VERSION or "1.0"
        self.environment = settings.ENVIRONMENT.value  # Enum -> string
        self.log_threshold = settings.LOG_RESPONSE_TIME_THRESHOLD
        self._static_headers = self._build_static_headers()

    def _build_static_headers(self) -> Dict[str, str]:
        """
        Headers that don't change per request.
        Adds HSTS for production/staging.
        """
        headers = {
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "X-Permitted-Cross-Domain-Policies": "none",
            "Content-Security-Policy": "default-src 'self'",
            "X-API-Version": self.api_version,
            "X-Environment": self.environment,
        }

        if self.environment in ["production", "staging"]:
            headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains; preload"
            )

        return headers

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        start_time = time.time()

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(f"Request {request_id} failed: {exc}", exc_info=True)
            return self._build_error_response(request_id)

        process_time = time.time() - start_time
        self._add_response_headers(response, request_id, process_time)

        # Logging request details
        log_data = {
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "process_time_ms": round(process_time * 1000, 2),
            "request_id": request_id,
            "request_size": request.headers.get("content-length"),
            "response_size": response.headers.get("content-length"),
        }

        log_request(logger, log_data)

        # Log slow requests
        if process_time > self.log_threshold:
            log_slow_request(logger, log_data)

        return response

    def _add_response_headers(self, response: Response, request_id: str, process_time: float):
        """
        Adds security headers, request ID, and processing time.
        """
        response.headers.update(self._static_headers)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

    def _build_error_response(self, request_id: str) -> JSONResponse:
        """
        Builds a standard error response in case of exceptions.
        """
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "request_id": request_id},
            headers={**self._static_headers, "X-Request-ID": request_id},
        )
