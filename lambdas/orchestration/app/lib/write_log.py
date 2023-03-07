import os

from .absolute_file_path import absolute_file_path
from .get_logbase import LogbaseError, parse_log_base

LOG_CONFIG = parse_log_base(os.path.join(absolute_file_path(__file__), "logbase.cfg"))


class LogRefNotFound(LogbaseError):
    """Exception to raise if attempted log is not in logbase"""


class MissingVariables(LogbaseError):
    """Exception to raise if incomplete log dict passed to log"""


def write_log(log_ref, log_dict):
    # Find log
    log = LOG_CONFIG.get(log_ref)
    if not log:  # pragma: no cover
        raise LogRefNotFound(f"Log with Ref={log_ref} not found in logbase")

    # Level
    level = log["level"]

    # Text
    try:
        log_text = log["text"]
        text = log_text.format(**log_dict)
    except KeyError as exc:  # pragma: no cover
        raise MissingVariables(
            f"Missing variables passed to log with text={log_text} log_dict={log_dict}"
        ) from exc
    print(f"Ref={log_ref} Level={level} {text}")
