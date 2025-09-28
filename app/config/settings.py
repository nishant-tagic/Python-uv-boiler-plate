from enum import Enum
from typing import List
import os

class Environment(str, Enum):
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"

class SecurityConfig:
    """All security and CORS related configuration"""

    def __init__(self):
        # Environment
        self.environment: Environment = Environment(os.getenv("ENVIRONMENT", "dev"))

        # API version
        self.api_version: str = os.getenv("API_VERSION", "1.0")

        # CORS origins
        self.cors_origins: List[str] = [
            "https://dev10bn.tataaig.com",
            "https://alpha10bn.tataaig.com"
        ]

        # Trusted hosts
        self.trusted_hosts: List[str] = [
            "localhost",
            "127.0.0.1",
            "0.0.0.0"
        ]

        # HSTS
        self.hsts_max_age: int = int(os.getenv("HSTS_MAX_AGE", "31536000"))

        # Logging thresholds
        self.log_response_time_threshold: float = float(os.getenv("LOG_RESPONSE_TIME_THRESHOLD", "1.0"))

        # Feature toggles
        self.enable_request_logging: bool = os.getenv("ENABLE_REQUEST_LOGGING", "true").lower() == "true"
