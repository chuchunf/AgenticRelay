import json
import logging
import os

from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):

    def format(self, record):
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        if hasattr(record, 'context') and record.context:
            log_entry["context"] = record.context

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry)

class Logger:

    def __init__(self, name: str = "relay", log_level: str = "INFO", log_file: Optional[str] = None):
        self.name = name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.log_file = log_file
        self._logger = logging.getLogger(name)
        self._setup_logger()

    def debug(self, message: str, **context) -> None:
        self._log(logging.DEBUG, message, context)

    def info(self, message: str, **context) -> None:
        self._log(logging.INFO, message, context)

    def warning(self, message: str, **context) -> None:
        self._log(logging.WARNING, message, context)

    def error(self, message: str, **context) -> None:
        self._log(logging.ERROR, message, context)

    def critical(self, message: str, **context) -> None:
        self._log(logging.CRITICAL, message, context)

    def _setup_logger(self):
        self._logger.handlers.clear()
        self._logger.setLevel(self.log_level)

        json_formatter = JSONFormatter()

        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(json_formatter)
        self._logger.addHandler(console_handler)

        if self.log_file:
            log_dir = os.path.dirname(self.log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir)

            file_handler = RotatingFileHandler(
                self.log_file,
                maxBytes=10*1024*1024,
                backupCount=5
            )
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(json_formatter)
            self._logger.addHandler(file_handler)

        self._logger.propagate = False

    def _log(self, level: int, message: str, context: Dict[str, Any]) -> None:
        record = self._logger.makeRecord(
            name=self._logger.name,
            level=level,
            fn="",
            lno=0,
            msg=message,
            args=(),
            exc_info=None
        )

        if context:
            record.context = context

        self._logger.handle(record)