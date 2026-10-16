import logging
import json
from datetime import datetime, timezone
from typing import Any, Dict
import uuid


class JSONFormatter(logging.Formatter):
    """Structured JSON logger that redacts sensitive fields."""
    
    SENSITIVE_KEYS = {"password", "token", "secret", "credential", "rtsp_url", "auth"}
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": self._redact(record.getMessage()),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        if hasattr(record, "request_id"):
            log_entry["request_id"] = record.request_id
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)
    
    def _redact(self, message: str) -> str:
        # Basic redaction: do not log RTSP URLs with passwords
        import re
        return re.sub(r'rtsp://[^:]+:[^@]+@', 'rtsp://***:***@', message)


def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=level, handlers=[handler])
    # Quieten noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
