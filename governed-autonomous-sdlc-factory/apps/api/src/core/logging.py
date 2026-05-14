"""Structured JSON logging configuration."""
import logging
import sys
import json
from datetime import datetime, timezone
from typing import Optional

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.now(timezone.utc).isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["source"] = {
            "file": record.pathname,
            "line": record.lineno,
            "function": record.funcName,
        }


def setup_logging(log_level: str = "INFO", log_format: str = "json"):
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)

    if log_format == "json":
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Reduce noise from third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


class StructuredLog:
    """Helper to create structured log entries with all required fields."""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def log(
        self,
        severity: str,
        message: str,
        run_id: Optional[str] = None,
        phase_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        task_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        source_file: Optional[str] = None,
        commit_hash: Optional[str] = None,
        **extra,
    ):
        entry = {
            "message": message,
            "severity": severity,
            "run_id": run_id,
            "phase_id": phase_id,
            "agent_id": agent_id,
            "task_id": task_id,
            "trace_id": trace_id,
            "source_file": source_file,
            "commit_hash": commit_hash,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        entry.update(extra)
        # Remove None values
        entry = {k: v for k, v in entry.items() if v is not None}

        level_map = {
            "critical": logging.CRITICAL,
            "error": logging.ERROR,
            "warning": logging.WARNING,
            "info": logging.INFO,
            "debug": logging.DEBUG,
        }
        level = level_map.get(severity.lower(), logging.INFO)
        self.logger.log(level, json.dumps(entry))
        return entry
