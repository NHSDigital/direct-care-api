import pytest

from ...lib.write_log import write_log
from ..utils.log_helper import LogHelper


def test_write_log_success(logger: LogHelper):

    write_log("LAMBDA0001", {"event": "mocked_event"})

    assert logger.was_logged("LAMBDA0001")

    assert logger.was_value_logged("LAMBDA0001", "event", "mocked_event")


def test_write_log_log_ref_not_found():

    with pytest.raises(ValueError):
        write_log("INVALIDLOG", {"event": {"key": "value"}})


def test_multiple_write_log(logger: LogHelper):

    for _ in range(3):
        write_log("LAMBDA0001", {"event": {"key": "value"}})

    assert logger.logged_number_of_times("LAMBDA0001", 3)
