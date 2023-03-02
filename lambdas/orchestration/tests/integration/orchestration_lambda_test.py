from ...app.orchestration_handler import orchestration_handler
from ..utils.log_helper import LogHelper
from ..utils.test_utils import mock_orchestration_event, parse_response


def test_orchestration_lambda_success(logger: LogHelper):

    nhs_number = "9999999999"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(orchestration_handler(event, ""))

    assert lambda_response.status_code == 200
    assert lambda_response.body == {'nhs_number': nhs_number}

    assert logger.was_logged("LAMBDA0001")


def test_orchestration_lambda_no_nhs_number_provided(logger: LogHelper):

    nhs_number = None

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(orchestration_handler(event, ""))

    expected_error = "nhs_number is required query string parameter"

    assert lambda_response.status_code == 400
    assert lambda_response.body == {"error": expected_error}

    assert logger.was_logged("LAMBDA0001")

    assert logger.was_logged("LAMBDA0002")
    assert logger.was_value_logged(
        "LAMBDA0002",
        "reason",
        "nhs_number is required query string parameter"
    )
