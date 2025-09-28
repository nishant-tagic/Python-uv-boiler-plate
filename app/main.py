import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from app.config.settings import Environment, SecurityConfig
from app.middleware.cors import setup_cors
from app.middleware.security import SecurityMiddleware
from app.core.logging import setup_logging, get_logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.health import router

# Load config
config = SecurityConfig()

# Initialize FastAPI
app = FastAPI()

# Setup logging
setup_logging()
logger = get_logger(__name__)

# Setup middlewares
setup_cors(app, config)
app.add_middleware(SecurityMiddleware,
                   api_version=config.api_version,
                   environment=config.environment.value,
                   log_threshold=config.log_response_time_threshold)

# Add GZip middleware
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)

# Add TrustedHost middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.trusted_hosts)

# Uncomment if HTTPS redirect is needed
# app.add_middleware(HTTPSRedirectMiddleware)

# Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.exception(exc)
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": exc.detail}
    )

@app.exception_handler(Exception)
async def uncaught_exception_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception(exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Something went wrong, please try again later",
        },
    )

# Routes
@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {"Hello": "World"}

app.include_router(router)

if __name__ == "__main__":
    # Production server configuration
    uvicorn_config = {
        "app": "app.main:app",
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", "8000")),
        "log_level": "info",
        "access_log": config.enable_request_logging,
        "reload": config.environment == Environment.DEVELOPMENT,
    }
    
    # Additional production settings
    if config.environment == Environment.PRODUCTION:
        uvicorn_config.update({
            "workers": int(os.getenv("WORKERS", "4")),
        })
    
    uvicorn.run(**uvicorn_config)