from contextlib import suppress
from logging import Filter, LogRecord


class LambdaContextLoggingFilter(Filter):
    """
    A custom filter to enrich log records with properties obtained
    from the aws lambda context object.

    Log records are first tested against the known formats used by our logging implementation(s).
    If a match is found, then selected properties from the aws lambda context
    are added to the record in a compatible manner.
    """

    def __init__(self, context=None) -> None:
        super().__init__()
        self._context = context

    @property
    def context(self):
        return self._context

    @context.setter
    def context(self, context) -> None:
        self._context = context

    def filter(self, record: LogRecord) -> bool:
        with suppress(Exception):
            if self._is_string_based(record):
                record.args = {**record.args, **self._context_args()}  # type: ignore
            elif self._is_callable_based(record):
                record.args = [  # type: ignore
                    lambda args=record.args[0]: {**args(), **self._context_args()}  # type: ignore
                ]
        return True

    @staticmethod
    def _is_string_based(record: LogRecord) -> bool:
        return isinstance(record.msg, str) and record.args == {"message": record.msg}

    @staticmethod
    def _is_callable_based(record: LogRecord) -> bool:
        return (
            record.msg is None
            and isinstance(record.args, list)
            and len(record.args)
            and callable(record.args[0])
        )

    def _context_args(self) -> dict:
        return (
            {}
            if self._context is None
            else {"aws_request_id": getattr(self._context, "aws_request_id", "unknown")}
        )
