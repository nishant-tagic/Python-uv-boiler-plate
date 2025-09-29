from enum import Enum
from pydantic_settings import BaseSettings
from pydantic import SecretStr
from typing import List

class EnvironmentOption(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    UAT = "uat"
    PRODUCTION = "production"

class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "FastAPI app"
    APP_DESCRIPTION: str | None = None
    APP_VERSION: str | None = None
    LICENSE_NAME: str | None = None
    CONTACT_NAME: str | None = None
    CONTACT_EMAIL: str | None = None

    # Environment
    ENVIRONMENT: EnvironmentOption = EnvironmentOption.LOCAL
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    TRUSTED_HOSTS: List[str] = ["localhost"]
    LOG_RESPONSE_TIME_THRESHOLD: float = 2.0
    ENABLE_REQUEST_LOGGING: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
