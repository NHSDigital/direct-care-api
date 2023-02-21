# pylint: disable=C0116, C0115, C0114
import logging
import sys
from typing import List

from .formatters import StructuredFormatter, JSONFormatter

# pylint: disable=C0301
_filter_are_errors = staticmethod(lambda r: r.levelno >= logging.ERROR)  # type: ignore [no-any-return]
_filter_not_errors = staticmethod(lambda r: r.levelno < logging.ERROR)  # type: ignore [no-any-return]


class CapturingHandler(logging.Handler):
    def __init__(self, messages: List[dict], level=logging.NOTSET):
        super().__init__(level)
        self.messages = messages
        self.formatter = StructuredFormatter()

    def emit(self, record: logging.LogRecord):
        log = self.format(record)

        self.messages.append(log)  # type: ignore [arg-type]


def capturing_log_handlers(stdout_cap: List[dict], stderr_cap: List[dict]):
    stdout_handler = CapturingHandler(stdout_cap)
    stdout_handler.addFilter(
        type("", (logging.Filter,), {"filter": _filter_not_errors})
    )

    stderr_handler = CapturingHandler(stderr_cap)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.addFilter(
        type("", (logging.Filter,), {"filter": _filter_are_errors})
    )

    return [stdout_handler, stderr_handler]


def sys_std_handlers():
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(JSONFormatter())
    stdout_handler.addFilter(
        type("", (logging.Filter,), {"filter": _filter_not_errors})
    )

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setLevel(logging.ERROR)
    stderr_handler.setFormatter(JSONFormatter())
    stderr_handler.addFilter(
        type("", (logging.Filter,), {"filter": _filter_are_errors})
    )

    return [stdout_handler, stderr_handler]
