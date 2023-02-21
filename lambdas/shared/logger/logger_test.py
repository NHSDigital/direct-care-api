# pylint: disable=C0116, C0115, C0114
import logging
from typing import Generator, Iterable, List, Tuple
import pytest
from pydantic import BaseModel


from shared.logger import (
    action_logging,
    add_fields,
    Constants,
    log_action,
    LogLevel,
    logging_context,
)
from .logger import app_logger
from .handlers import capturing_log_handlers


@pytest.fixture(scope="function", name="log_capture")
def fixture_log_capture(log_capture_global) -> Iterable[Tuple[List[dict], List[dict]]]:
    std_out, std_err = log_capture_global

    std_out.clear()
    std_err.clear()

    log_at_level = app_logger.log_at_level

    app_logger.log_at_level = LogLevel.DEBUG

    yield std_out, std_err

    app_logger.log_at_level = log_at_level


@pytest.fixture(scope="session", name="log_capture_global")
def fixture_log_capture_global() -> Iterable[Tuple[List[dict], List[dict]]]:
    std_out = []  # type: ignore [var-annotated]
    std_err = []  # type: ignore [var-annotated]

    capturing_handlers = capturing_log_handlers(std_out, std_err)

    app_logger.setup("tests")

    for handler in capturing_handlers:
        logging.root.addHandler(handler)

    yield std_out, std_err

    for handler in capturing_handlers:
        logging.root.removeHandler(handler)


class TestExplodingModel(BaseModel):
    name: str


def test_logging_simple(log_capture):
    std_out, std_err = log_capture

    app_logger.info(lambda: {"test": 123})

    assert 1 == len(std_out)
    assert 0 == len(std_err)
    assert 123 == std_out[0]["test"]


def test_logging_simple_is_lazy(log_capture):
    std_out, std_err = log_capture

    prev_level = app_logger.log_at_level

    try:
        app_logger.log_at_level = logging.WARN

        calls = []

        def create_logging_args():
            calls.append(1)
            return {"things": 123}

        app_logger.info(create_logging_args)

        assert 0 == len(std_out)
        assert 0 == len(std_err)
        assert 0 == len(calls)
    finally:
        app_logger.log_at_level = prev_level


def test_logging_default_logger(log_capture):
    std_out, std_err = log_capture
    level = logging.root.level
    logging.root.setLevel(LogLevel.INFO)
    logging.info("test")
    logging.root.setLevel(level)
    assert 0 == len(std_err)
    assert "test" == std_out[0]["message"]


def test_log_exception(log_capture):
    std_out, std_err = log_capture

    try:
        raise ValueError("testing")
    except ValueError:
        app_logger.exception(lambda: {"things": 123})

    assert 0 == len(std_out)
    assert 1 == len(std_err)

    err = std_err[0]
    assert "testing" == err["ex"]
    assert "builtins.ValueError" == err["ex_type"]


def test_with_action_logging(log_capture):
    std_out, std_err = log_capture

    with action_logging(field=123):
        num = 1 + 1

        add_fields(num=num)

    assert 0 == len(std_err)
    assert 1 == len(std_out)

    log = std_out[0]

    assert 2 == log["num"]
    assert 123 == log["field"]

    assert Constants.TASK_UUID_FIELD in log


def test_with_action_logging_exploded_model(log_capture):
    std_out, std_err = log_capture

    with action_logging(field=TestExplodingModel(name="vic")):
        num = 1 + 1

        add_fields(num=num)

    assert 0 == len(std_err)
    assert 1 == len(std_out)

    log = std_out[0]

    assert 2 == log["num"]

    assert isinstance(
        log["field"].dict(), dict
    ), "Model was not exploded to primitive form!"
    assert "vic" == log["field"].dict()["name"]

    assert Constants.TASK_UUID_FIELD in log


def test_with_action_logging_exploded_model_added_after(log_capture):
    std_out, std_err = log_capture

    with action_logging(field=123):
        add_fields(obj=TestExplodingModel(name="vic"))

    assert 0 == len(std_err)
    assert 1 == len(std_out)

    log = std_out[0]

    assert 123 == log["field"]

    assert isinstance(
        log["obj"].dict(), dict
    ), "Model was not exploded to primitive form!"
    assert "vic" == log["obj"].dict()["name"]

    assert Constants.TASK_UUID_FIELD in log


def test_with_action_logging_exception(log_capture):
    _, std_err = log_capture

    try:
        with action_logging(field=123):
            num = 1 + 1

            add_fields(num=num)

            raise ValueError("Test")

    except ValueError:
        pass

    assert 1 == len(std_err)

    log = std_err[0]

    assert 2 == log["num"]
    assert 123 == log["field"]

    assert Constants.TASK_UUID_FIELD in log


def test_log_action(log_capture):
    std_out, _ = log_capture

    @log_action()
    def test_function():
        add_fields(field=123)

    test_function()

    assert 1 == len(std_out)

    log = std_out[0]

    assert 123 == log["field"]

    assert "test_function" == log[Constants.ACTION_FIELD]
    assert Constants.SUCCEEDED_STATUS == log[Constants.ACTION_STATUS_FIELD]


def test_log_action_with_args(log_capture):
    std_out, _ = log_capture

    @log_action(log_args=["_bob"])
    def test_function(_bob):
        add_fields(field=123)

    test_function("vic")

    assert 1 == len(std_out)

    log = std_out[0]

    assert 123 == log["field"]

    assert "test_function" == log[Constants.ACTION_FIELD]
    assert Constants.SUCCEEDED_STATUS == log[Constants.ACTION_STATUS_FIELD]

    assert "vic" == log["_bob"]


def test_log_action_with_model_exploded(log_capture):
    std_out, _ = log_capture

    @log_action(log_args=["_bob"])
    def test_function(_bob):
        add_fields(field=123)

    test_function(TestExplodingModel(name="vic"))

    assert 1 == len(std_out)

    log = std_out[0]

    assert 123 == log["field"]

    assert "test_function" == log[Constants.ACTION_FIELD]
    assert Constants.SUCCEEDED_STATUS == log[Constants.ACTION_STATUS_FIELD]

    assert isinstance(
        log["_bob"].dict(), dict
    ), "Model was not exploded to primitive form!"
    assert "vic" == log["_bob"].dict()["name"]


def test_log_action_with_named_action(log_capture):
    std_out, _ = log_capture

    @log_action(action="test", log_args=["_bob"])
    def test_function(_bob):
        add_fields(field=123)

    test_function("vic")

    assert 1 == len(std_out)

    log = std_out[0]

    assert 123 == log["field"]

    assert "test" == log[Constants.ACTION_FIELD]
    assert Constants.SUCCEEDED_STATUS == log[Constants.ACTION_STATUS_FIELD]

    assert "vic" == log["_bob"]


def test_log_action_exception(log_capture):
    _, std_err = log_capture

    @log_action()
    def test_function():
        add_fields(field=123)
        raise ValueError("eek")

    try:
        test_function()
    except ValueError:
        pass

    assert 1 == len(std_err)

    log = std_err[0]

    assert 123 == log["field"]

    assert "test_function" == log[Constants.ACTION_FIELD]
    assert Constants.FAILED_STATUS == log[Constants.ACTION_STATUS_FIELD]


def test_generator():
    @log_action()
    def inner_action() -> str:
        action = logging_context.current()
        return action.task_uuid  # type: ignore [no-any-return, union-attr]

    @log_action()
    def generator_action(count: int) -> Generator[str, str, None]:
        for _ in range(count):
            # pylint: disable=C0301
            yield logging_context.current().task_uuid, inner_action(), None  # type: ignore [union-attr, misc]

    @log_action()
    def outer_action():
        res = list(generator_action(3))
        action = logging_context.current()
        return action.task_uuid, res

    result = outer_action()

    print(result)
