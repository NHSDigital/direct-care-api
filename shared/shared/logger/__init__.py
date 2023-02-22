# pylint: disable=C0116, C0115, C0114
import inspect
import logging
from contextlib import contextmanager
from functools import wraps
from inspect import BoundArguments
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from .caller_info import find_caller_info
from .constants import Constants
from .context import logging_context
from .logger import app_logger as _app_logger

DEFAULT_LOG_LEVEL = Constants.DEFAULT_LOG_LEVEL
LOG_AT_LEVEL = Constants.LOG_AT_LEVEL
LOG_LEVEL = Constants.LOG_LEVEL


# levels


class LogLevel:  # pylint: disable=R0903
    CRITICAL = logging.CRITICAL
    FATAL = CRITICAL
    ERROR = logging.ERROR
    AUDIT = logging.WARN
    WARNING = logging.WARN
    WARN = WARNING
    NOTICE = 25
    INFO = logging.INFO
    DEBUG = logging.DEBUG
    TRACE = 5


app_logger = _app_logger

action_logging = logging_context.start_action


def add_fields(**kwargs):
    """Add success fields to the current action

    Args:
        **kwargs: fields to be added
    """
    action = logging_context.current()
    if action:
        action.add_fields(**kwargs)
    else:
        raise ValueError("Add fields called with no current action")


def debug_fields(fun_fields: Callable[[], dict]):
    """Add success fields to the current action

    Args:
        fun_fields (Callable[dict]): factory to create fields on demand
    """
    action = logging_context.current()
    if action:
        if logging_context.log_at_level() <= logging.DEBUG:
            fields = fun_fields()
            action.add_fields(**fields)
    else:
        raise ValueError("Add fields called with no current action")


def log_stacktrace(**fields):
    """
    Write the latest traceback to the log.

    This should be used inside an C{except} block. For example:

         try:
             dostuff()
         except:
             writeTraceback(logger)
    """
    fields[Constants.LOG_LEVEL] = fields.get(Constants.LOG_LEVEL, logging.ERROR)
    logging_context.log_exception(**fields)


def get_args_map(func, *args, **kwargs):
    """Get a map of arguments to their argument name as defined by the function."""
    args_map = {}
    if args or kwargs:
        sig = inspect.Signature.from_callable(func)
        bound_args = sig.bind(*args, **kwargs)  # type: BoundArguments
        args_map.update(bound_args.arguments)

    return args_map


def get_method_name(func, *args, **kwargs):
    """
    Represent that name of a decorated function including the class name
    if it's a method on a class, otherwise just the function name.

    Args:
        f (function) - the function being decorated
        args - args
        kwargs - keyword arguments

    Returns
        method_name (string) - human readable representation of the function/method name
    """
    args_map = get_args_map(func, *args, **kwargs)
    if "self" in args_map:
        cls = args_map["self"].__class__
        method_name = f"{cls.__name__}.{func.__name__}"
    elif "cls" in args_map:
        cls = args_map["cls"]
        method_name = f"{cls.__name__}.{func.__name__}"
    else:
        method_name = func.__name__
    return method_name


def get_args(arg_list, func, *args, **kwargs):
    """Returns a dictionary of the specified arguments keyed against their argument name."""
    args_map = get_args_map(func, *args, **kwargs)
    if not arg_list or not args_map:
        return {}
    specific_args = {k: v for k, v in args_map.items() if k in arg_list}
    return specific_args


def log_action(
    action: Optional[str] = None,
    log_level: Optional[Union[str, int]] = None,
    log_args: Optional[List[str]] = None,
    **other_log_args,
):
    """Decorator to wrap execution of the main entry points for each pipeline stage's processing.

    Decorator usage must always call this as a function even if no arguments are provided.

    If decorating a class method, ensure that `@classmethod` decorator comes first.

    Examples:
        @log_action(action='example_action')
        @log_action(log_args=['argument_to_log'])
        @log_action(action='example_action', log_args=['argument_to_log'])
        @log_action()

    Args:
        action (str) - human readable string of the type of action being carried out to populate the
                      `action` field in the log message.
                      If not provided defaults to the method name
        log_level: (LogLevels._LogLevel): level to log messages at
        log_args (list(string)) - list of arguments that should be logged. D
            efaults to empty list, i.e. log none.
        other_log_args (dict): other log args
    Returns:
        decorated function
    """
    if not log_args:
        log_args = []

    def _log_action(func):
        """Nested decorator.

        Args:
            f (function) - the function to be wrapped
        Returns:
            decorated function
        """

        def _get_log_args(
            wrapper, *args, **kwargs
        ) -> Tuple[str, tuple, Dict[str, Any]]:
            caller_inf = find_caller_info(wrapper, True)

            method_name = get_method_name(func, *args, **kwargs)
            args_to_log = get_args(log_args, func, *args, **kwargs)

            if other_log_args:
                args_to_log.update(other_log_args)

            action_name = action or method_name

            if log_level:
                args_to_log[Constants.LOG_LEVEL] = log_level

            return action_name, caller_inf, args_to_log

        @wraps(func)
        def _process_wrapper(*args, **kwargs):
            action_name, caller_inf, args_to_log = _get_log_args(
                _process_wrapper, *args, **kwargs
            )

            with action_logging(
                action=action_name, caller_info=caller_inf, **args_to_log
            ):
                result = func(*args, **kwargs)

            return result

        @wraps(func)
        async def _async_process_wrapper(*args, **kwargs):
            action_name, caller_inf, args_to_log = _get_log_args(
                _async_process_wrapper, *args, **kwargs
            )

            with action_logging(
                action=action_name, caller_info=caller_inf, **args_to_log
            ):
                result = await func(*args, **kwargs)

            return result

        return (
            _async_process_wrapper
            if inspect.iscoroutinefunction(func)
            else _process_wrapper
        )

    return _log_action


@contextmanager
def add_temporary_global_fields(**kwargs):
    """
    Method for adding a field to every message logged
    within the scope of this context manager
    """
    fields = kwargs.keys()
    logging_context.add_global_fields(**kwargs)
    try:
        yield
    finally:
        # There is no public method for removing global fields in eliot
        # Failing to remove the field would cause it to be wrongly logged against some messages
        for field in fields:
            logging_context.remove_global_field(field)
