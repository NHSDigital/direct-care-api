# pylint: disable=C0115, C0114
import json
import logging
import traceback
from collections import OrderedDict
from datetime import date, datetime

from ..version_data import FULL_VERSION_STRING


def json_serializer(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if isinstance(obj, type) or callable(obj):
        return repr(obj)

    return str(repr(obj))


class StructuredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> dict:  # type: ignore [override]
        log = OrderedDict()

        log.update(
            {
                "timestamp": datetime.fromtimestamp(record.created).timestamp(),
                "level": record.levelname,
            }
        )

        if record.args:
            args = record.args

            if isinstance(args, list) and callable(args[0]):
                args = args[0]()
            elif not isinstance(args, dict):
                args = {"args": record.args}

            if args:
                rec_ts = args.get("timestamp")
                if rec_ts:
                    # pylint: disable=C0301
                    args["timestamp"] = datetime.fromtimestamp(rec_ts).timestamp()  # type: ignore [arg-type]

                log.update(args)

        log_info = {
            "logger": record.name,
            "level": record.levelname,
            "path": record.pathname,
            "module": record.module,
            "line_no": record.lineno,
            "func": record.funcName,
            "filename": record.filename,
            "pid": record.process,
            "version": FULL_VERSION_STRING,
        }

        if record.thread:
            log_info["thread"] = record.thread
            log_info["thread_name"] = record.threadName

        if record.processName:
            log_info["process_name"] = record.processName

        if record.msg:
            log["message"] = record.getMessage()

        log["log_inf"] = log_info

        exc_info = record.__dict__.get("exc_info", None)

        if exc_info:
            _, exc, _ = exc_info

            log["ex_type"] = f"{exc.__class__.__module__}.{exc.__class__.__name__}"

            if exc.__cause__:
                log["ex_cause"] = exc.__cause__

            log["ex"] = str(exc)

            log["ex_tb"] = "".join(traceback.format_tb(exc.__traceback__))

            log_info["stack_info"] = record.stack_info

        return log


class JSONFormatter(StructuredFormatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore [override]
        record = super().format(record)  # type: ignore [assignment]

        return f"{json.dumps(record, default=json_serializer)}\n"
