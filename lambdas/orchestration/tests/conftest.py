# pylint: disable=unused-argument

import logging
from unittest.mock import patch

import pytest

from .utils.log_helper import LogHelper
from .utils.mock_get_request import MockGetRequest
from .utils.mock_post_request import MockPostRequest
from .utils.mock_ssm_client import MockSSMClient


@pytest.fixture(name="logger")
def log_helper_fixture(request):
    """For tests that require log capture, use our log_helper to capture all logs"""
    logging.disable(logging.CRITICAL)
    log_helper = LogHelper(request.node.originalname)
    log_helper.set_stdout_capture()
    return log_helper


@pytest.fixture(autouse=True)
def patch_ssm():
    with patch("lambdas.orchestration.app.lib.get_ssm_param.get_ssm_client", MockSSMClient()):
        yield


@pytest.fixture(autouse=True)
def patch_get_request():
    with patch("lambdas.orchestration.app.lib.make_request.requests.get", MockGetRequest()):
        yield


@pytest.fixture(autouse=True)
def patch_post_request():
    with patch("lambdas.orchestration.app.lib.make_request.requests.post", MockPostRequest()):
        yield
