import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config.config import Settings, EnvironmentOption
from app.middleware.cors import setup_cors
from app.middleware.security import SecurityMiddleware
from app.core.logging import setup_logging, get_logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.api.health import router

# Load configuration
config = Settings()

# Initialize FastAPI
app = FastAPI(
    title=config.APP_NAME,
    description=config.APP_DESCRIPTION,
    version=config.APP_VERSION
)

# Setup logging
setup_logging()
logger = get_logger(__name__)

# --- Middleware Setup ---

# 1. CORS
setup_cors(app, config)

# 2. Security Middleware
app.add_middleware(SecurityMiddleware)

# 3. Trusted Hosts
if config.ENVIRONMENT in [EnvironmentOption.PRODUCTION, EnvironmentOption.UAT]:
    allowed_hosts = list(config.TRUSTED_HOSTS)
else:
    allowed_hosts = ["*"]

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=list(config.TRUSTED_HOSTS)
)

# 4. GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000, compresslevel=5)


# --- Exception Handlers ---

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

# --- Routes ---

@app.get("/")
def root():
    logger.info("Root endpoint called")
    return {"Hello": "World"}

# Include API router
app.include_router(router)

# --- Run Uvicorn ---

if __name__ == "__main__":
    uvicorn_config = {
        "app": "app.main:app",
        "host": "0.0.0.0",
        "port": int(os.getenv("PORT", "8000")),
        "log_level": "debug" if config.ENVIRONMENT in [EnvironmentOption.LOCAL, EnvironmentOption.DEV] else "info",
        "access_log": config.ENABLE_REQUEST_LOGGING,
        "reload": config.ENVIRONMENT in [EnvironmentOption.LOCAL, EnvironmentOption.DEV],
    }

    logger.info(f"Starting FastAPI app in {config.ENVIRONMENT} environment")
    uvicorn.run(**uvicorn_config)
