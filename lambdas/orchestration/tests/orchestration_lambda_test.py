from lambdas.orchestration.orchestration_handler import orchestration_handler
from lambdas.orchestration.tests.utils.test_utils import (
    mock_orchestration_event,
    parse_response,
)


def test_orchestration_lambda_success():

    nhs_number = "9999999999"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(orchestration_handler(event, ""))

    assert lambda_response.status_code == 200
    assert lambda_response.body == {'nhs_number': nhs_number}


def test_orchestration_lambda_no_nhs_number_provided():

    nhs_number = None

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(orchestration_handler(event, ""))

    assert lambda_response.status_code == 400
    assert lambda_response.body == {"error": "nhs_number is required query string parameter"}
