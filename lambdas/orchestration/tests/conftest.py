# pylint: disable=unused-argument

import logging

import pytest

from .utils.log_helper import LogHelper


@pytest.fixture(name="logger")
def log_helper_fixture(request):
    """For tests that require log capture, use our log_helper to capture all logs"""
    logging.disable(logging.CRITICAL)
    log_helper = LogHelper(request.node.originalname)
    log_helper.set_stdout_capture()
    return log_helper
