# --- DNK-MRH-HEADER ---
# mrh_id: "packages/utils/logging.py"
# purpose: "Canonical Structured JSON logging utilities for DNK OS"
# canonical_source: true
# alters_files: []
# triggers_tasks: []
# status: "Active"
# version: "2.0.0"
# updated_at: "2026-09-15"
# author: "DNK-e.com Maksym"
# --- END DNK-MRH-HEADER ---

"""Structured logging utilities for DNK OS."""

import logging
import json
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record as JSON.
        
        Args:
            record: Log record
            
        Returns:
            JSON-formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Setup structured JSON logging.
    
    Args:
        level: Log level
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger("dnk_os")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid duplicate handlers if already configured
    if not logger.handlers:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(JSONFormatter())
        logger.addHandler(console_handler)
    else:
        for handler in logger.handlers:
            handler.setFormatter(JSONFormatter())
            
    return logger
