"""Structured logging configuration for qchem-stack.

This module provides JSON-formatted structured logging for production deployments.
Enable by setting the environment variable QCHEM_STACK_LOG_FORMAT=json.

Example output:
    {"timestamp": "2026-05-29T15:30:45.123Z", "level": "INFO", "name": "qchem_stack.orchestration", "message": "Pipeline started", "experiment_id": "h2_vqe_001"}

Usage:
    # Explicit initialization (recommended)
    from qchem_stack._logging import configure_logging
    configure_logging()

    # Or via package init (lazy)
    import qchem_stack  # calls configure_logging() once
"""

from __future__ import annotations

import json
import logging
import os
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    Converts log records to JSON format with ISO 8601 timestamps and
    structured fields for easier parsing by log aggregation systems.
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def format(self, record: logging.LogRecord) -> str:
        """Format a log record as JSON."""
        log_obj: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }

        # Add optional fields if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        if record.stack_info:
            log_obj["stack_info"] = self.formatStack(record.stack_info)

        # Add extra fields from record.__dict__
        # Standard fields to exclude
        standard_fields = {
            "name",
            "msg",
            "args",
            "created",
            "relativeCreated",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "pathname",
            "filename",
            "module",
            "levelno",
            "levelname",
            "thread",
            "threadName",
            "process",
            "processName",
            "msecs",
            "message",
            "asctime",
        }

        for key, value in record.__dict__.items():
            if key not in standard_fields and not key.startswith("_"):
                # Convert non-serializable types to strings
                try:
                    json.dumps(value)
                    log_obj[key] = value
                except (TypeError, ValueError):
                    log_obj[key] = str(value)

        return json.dumps(log_obj, ensure_ascii=False)


def configure_logging() -> None:
    """Configure logging based on environment variables.

    This function is NOT called automatically on import. Call it explicitly
    from your application entry point or rely on the lazy initialization
    in ``qchem_stack/__init__.py``.

    Environment variables:
        QCHEM_STACK_LOG_FORMAT: 'json' for structured JSON logs, 'text' for plain text (default)
        QCHEM_STACK_LOG_LEVEL: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_format = os.getenv("QCHEM_STACK_LOG_FORMAT", "text").lower()
    log_level = os.getenv("QCHEM_STACK_LOG_LEVEL", "INFO").upper()

    # Get or create root logger for qchem_stack
    logger = logging.getLogger("qchem_stack")

    # Remove existing handlers
    logger.handlers.clear()

    # Create console handler
    handler = logging.StreamHandler(sys.stderr)

    # Set formatter based on environment
    if log_format == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set log level
    level = getattr(logging, log_level, logging.INFO)
    logger.setLevel(level)

    # Prevent propagation to root logger
    logger.propagate = False
