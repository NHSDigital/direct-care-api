# pylint: disable=C0114
import io
import logging
import os
import traceback
from typing import Callable, Tuple, Union


def find_caller_info(
    caller_of: Union[Callable, None] = None, stack_info: bool = False
) -> Tuple[str, int, str, Union[str, None]]:
    """cloned from python logger to allow caller info from app logger context

    Args:
        caller_of (function): function to find the caller of
        stack_info (bool): whether to include the stack info

    Returns:
        Tuple[str, int, str, Union[str, None]]: tuple filename, line number, function , stack info
    """

    try:
        return _find_caller_info(caller_of, stack_info)  # type: ignore [no-any-return]
    except ValueError:  # pragma: no cover
        return "(unknown file)", 0, "(unknown function)", None


def _find_caller_info(
    caller_of: Union[Callable, None] = None, stack_info: bool = False
):
    """cloned from python logger to allow caller info from app logger context

    Args:

        caller_of (function): function to find the caller of
        stack_info (bool): whether to include the stack info

    Returns:
        Tuple[str, int, str, Union[str, None]]: tuple filename, line number, function , stack info
    """
    current_frame = logging.currentframe()

    callee_func = caller_of.__code__.co_name if caller_of else None
    callee_path = (
        os.path.normcase(caller_of.__code__.co_filename) if caller_of else None
    )

    if current_frame is not None:
        current_frame = current_frame.f_back  # type: ignore [assignment]

    while hasattr(current_frame, "f_code"):
        fco = current_frame.f_code
        filename = os.path.normcase(fco.co_filename)
        func_name = fco.co_name

        if callee_path and filename == callee_path:
            current_frame = current_frame.f_back  # type: ignore [assignment]
            if callee_func and callee_func == func_name:
                callee_path = None
            continue

        if (
            not callee_path
            and filename.startswith(logger_module)
            and not filename.endswith("logger_tests.py")
        ):
            current_frame = current_frame.f_back  # type: ignore [assignment]
            continue

        sinfo = None
        if stack_info:
            sio = io.StringIO()
            sio.write("Stack (most recent call last):\n")
            traceback.print_stack(current_frame, file=sio)
            sinfo = sio.getvalue()
            if sinfo[-1] == "\n":
                sinfo = sinfo[:-1]
            sio.close()

        return fco.co_filename, current_frame.f_lineno, fco.co_name, sinfo

    return "(unknown file)", 0, "(unknown function)", None


logger_module = os.path.dirname(
    os.path.normcase(_find_caller_info.__code__.co_filename)
)
