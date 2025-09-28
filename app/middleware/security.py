import time
import uuid
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict

from app.core.logging import get_logger, log_request, log_slow_request

logger = get_logger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Handles security headers, request logging, slow requests, and request IDs.
    """

    def __init__(self, app, *, api_version="1.0", environment="dev", log_threshold=1.0):
        super().__init__(app)
        self.api_version = api_version
        self.environment = environment
        self.log_threshold = log_threshold
        self._static_headers = self._build_static_headers()

    def _build_static_headers(self) -> Dict[str, str]:
        """Headers that don't change per request"""
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
        if self.environment in ["prod", "staging"]:
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        return headers

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        request.state.request_id = request_id

        try:
            response = await call_next(request)
        except Exception as exc:
            logger.error(f"Request {request_id} failed: {exc}", exc_info=True)
            return self._build_error_response(request_id)

        process_time = time.time() - start_time
        self._add_response_headers(response, request_id, process_time)

        # Log requests
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
        if process_time > self.log_threshold:
            log_slow_request(logger, log_data)

        return response

    def _add_response_headers(self, response: Response, request_id: str, process_time: float):
        response.headers.update(self._static_headers)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

    def _build_error_response(self, request_id: str) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "request_id": request_id},
            headers={**self._static_headers, "X-Request-ID": request_id},
        )
