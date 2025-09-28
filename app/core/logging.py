from loguru import logger
import sys
from typing import Dict, Any
import json

def setup_logging(log_level: str = "INFO") -> None:
    logger.remove()

    def custom_json_sink(message):
        record = message.record
        log_object = {
            "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S"),
            "level": record["level"].name,
            "message": record["message"],
        }

        # Add debugging info only for WARNING level and above
        if record["level"].no >= 30:  # WARNING=30, ERROR=40, CRITICAL=50
            log_object.update({
                "module": record.get("module", ""),
                "function": record["function"],
                "line": record["line"],
            })

        # Add extra fields if any (e.g., request_id, path, etc.)
        if record["extra"]:
            log_object.update(record["extra"])

        print(json.dumps(log_object), flush=True)

    logger.add(
        custom_json_sink,
        level=log_level.upper(),
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )

def get_logger(name: str = None):
    """Return the Loguru logger. 'name' kept for compatibility."""
    return logger.bind(module=name) if name else logger

def log_request(logger_obj, request_data: Dict[str, Any]) -> None:
    """Log request information in a JSON structured format."""
    logger_obj.info({
        "event": "request_completed",
        "request_id": request_data.get("request_id"),
        "method": request_data.get("method"),
        "path": request_data.get("path"),
        "status_code": request_data.get("status_code"),
        "process_time": round(request_data.get("process_time", 0), 4),
        "client_ip": request_data.get("client_ip"),
    })

def log_slow_request(logger_obj, request_data: Dict[str, Any]) -> None:
    logger_obj.warning({
        "event": "slow_request_detected",
        "request_id": request_data.get("request_id"),
        "path": request_data.get("path"),
        "process_time": round(request_data.get("process_time", 0), 4),
    })

def log_rate_limit_exceeded(logger_obj, client_ip: str) -> None:
    logger_obj.debug({
        "event": "rate_limit_ignored",
        "message": "Rate limiting is disabled; call ignored",
        "client_ip": client_ip,
    })
