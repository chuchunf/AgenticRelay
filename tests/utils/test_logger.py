import json
import logging
import os
import tempfile
from unittest.mock import patch

from relay.utils.logger import Logger, JSONFormatter


class TestLogger:

    def test_logger_initialization(self):
        logger = Logger("test_logger")
        assert logger.name == "test_logger"
        assert logger.log_level == logging.INFO
        assert logger.log_file is None

    def test_logger_initialization_with_file(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            logger = Logger("test_logger", log_file=tmp_file.name)
            assert logger.log_file == tmp_file.name

            for handler in logger._logger.handlers[:]:
                handler.close()
                logger._logger.removeHandler(handler)

        os.unlink(tmp_file.name)

    def test_log_levels(self):
        logger = Logger("test_logger")

        with patch.object(logger._logger, 'handle') as mock_handle:
            logger.debug("debug message")
            logger.info("info message")
            logger.warning("warning message")
            logger.error("error message")
            logger.critical("critical message")

            assert mock_handle.call_count == 5

            calls = mock_handle.call_args_list
            assert calls[0][0][0].levelno == logging.DEBUG
            assert calls[1][0][0].levelno == logging.INFO
            assert calls[2][0][0].levelno == logging.WARNING
            assert calls[3][0][0].levelno == logging.ERROR
            assert calls[4][0][0].levelno == logging.CRITICAL

class TestJSONFormatter:

    def test_json_formatter_basic(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_logger"
        assert log_data["message"] == "test message"
        assert log_data["module"] == "test_module"
        assert log_data["function"] == "test_function"
        assert log_data["line"] == 1
        assert "timestamp" in log_data

    def test_json_formatter_with_context(self):
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="",
            lineno=1,
            msg="test message",
            args=(),
            exc_info=None
        )
        record.module = "test_module"
        record.funcName = "test_function"
        record.context = {"user_id": "123", "operation": "test"}

        result = formatter.format(record)
        log_data = json.loads(result)

        assert log_data["context"]["user_id"] == "123"
        assert log_data["context"]["operation"] == "test"
