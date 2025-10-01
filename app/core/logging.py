import json
from typing import Any

from loguru import logger

from app.config.config import EnvironmentOption

# Environment to log level mapping
ENV_LOG_LEVEL_MAP = {
    EnvironmentOption.LOCAL: "DEBUG",
    EnvironmentOption.DEV: "INFO",
    EnvironmentOption.UAT: "WARNING",
    EnvironmentOption.PRODUCTION: "WARNING",
}


def get_log_level_for_environment(environment: EnvironmentOption) -> str:
    """Get the appropriate log level for the given environment."""
    return ENV_LOG_LEVEL_MAP.get(environment, "INFO")


def setup_logging(environment: EnvironmentOption = None, log_level: str = None) -> None:
    """
    Setup logging with environment-based log levels.

    Args:
        environment: The environment option (will determine log level if log_level not provided)
        log_level: Explicit log level override (if provided, takes precedence over environment)
    """
    logger.remove()

    # Determine log level: explicit override > environment-based > default INFO
    if log_level:
        final_log_level = log_level.upper()
    elif environment:
        final_log_level = get_log_level_for_environment(environment)
    else:
        final_log_level = "INFO"

    def custom_json_sink(message):
        record = message.record
        log_object = {
            "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S"),
            "level": record["level"].name,
            "message": record["message"],
        }
        # Add debugging info only for WARNING level and above
        if record["level"].no >= 30:  # WARNING=30, ERROR=40, CRITICAL=50
            log_object.update(
                {
                    "module": record.get("module", ""),
                    "function": record["function"],
                    "line": record["line"],
                }
            )
        # Add extra fields if any (e.g., request_id, path, etc.)
        if record["extra"]:
            log_object.update(record["extra"])
        print(json.dumps(log_object), flush=True)

    logger.add(
        custom_json_sink,
        level=final_log_level,
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )

    # Log the logging configuration
    logger.debug(f"Logging initialized with level: {final_log_level}")


def get_logger(name: str = None):
    """Return the Loguru logger. 'name' kept for compatibility."""
    return logger.bind(module=name) if name else logger


def log_request(logger_obj, request_data: dict[str, Any]) -> None:
    """Log request information in a JSON structured format."""
    logger_obj.info(
        "request_completed",
        request_id=request_data.get("request_id"),
        method=request_data.get("method"),
        path=request_data.get("path"),
        status_code=request_data.get("status_code"),
        process_time=round(request_data.get("process_time", 0), 4),
        client_ip=request_data.get("client_ip"),
    )


def log_slow_request(logger_obj, request_data: dict[str, Any]) -> None:
    logger_obj.warning(
        "slow_request_detected",
        request_id=request_data.get("request_id"),
        path=request_data.get("path"),
        process_time=round(request_data.get("process_time", 0), 4),
    )


def log_rate_limit_exceeded(logger_obj, client_ip: str) -> None:
    logger_obj.debug(
        {
            "event": "rate_limit_ignored",
            "message": "Rate limiting is disabled; call ignored",
            "client_ip": client_ip,
        }
    )
