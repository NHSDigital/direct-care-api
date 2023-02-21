# pylint: disable=C0114
import inspect
from functools import wraps
import json
from requests import HTTPError, Response
from . import add_fields


def add_http_error_fields():
    """
    Decorator to wrap execution and add http error fields
    """

    def _wrapper(func):
        """Nested decorator.

        Args:
            f (function) - the function to be wrapped
        Returns:
            decorated function
        """

        @wraps(func)
        async def _async_process_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                return result

            except HTTPError as err:
                response = err.response  # type: Response
                add_fields(status_code=response.status_code)
                if not response.text:
                    raise
                try:
                    json_object = json.loads(response.text)
                    add_fields(response=json_object)
                except ValueError:
                    add_fields(response=response.text)
                raise

        @wraps(func)
        def _process_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                return result

            except HTTPError as err:
                response = err.response  # type: Response
                add_fields(status_code=response.status_code)
                if not response.text:
                    raise
                try:
                    json_object = json.loads(response.text)
                    add_fields(response=json_object)
                except ValueError:
                    add_fields(response=response.text)
                raise

        return (
            _async_process_wrapper
            if inspect.iscoroutinefunction(func)
            else _process_wrapper
        )

    return _wrapper
