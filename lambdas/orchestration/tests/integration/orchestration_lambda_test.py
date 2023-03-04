from ...app.orchestration_handler import orchestration_handler
from ..utils.log_helper import LogHelper
from ..utils.test_utils import mock_orchestration_event, parse_response


def test_orchestration_lambda_success(logger: LogHelper):
    nhs_number = "9999999999"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(orchestration_handler(event, ""))

    assert lambda_response.status_code == 200
    assert lambda_response.body["record"] == "D82021"

    assert logger.was_value_logged("PDS001", "nhs_number", nhs_number)

    assert logger.was_logged("LAMBDA001")


def test_orchestration_lambda_no_nhs_number_provided(logger: LogHelper):
    nhs_number = None

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(orchestration_handler(event, ""))

    expected_error = "nhs_number is required query string parameter"

    assert lambda_response.status_code == 400
    assert lambda_response.body["message"] == expected_error

    assert logger.was_logged("LAMBDA001")

    assert logger.was_logged("LAMBDA002")
    assert logger.was_value_logged(
        "LAMBDA002", "reason", "nhs_number is required query string parameter"
    )


def test_orchestration_lambda_nhs_number_is_invalid(logger: LogHelper):
    """Test case for when PDS fails to find the provided nhs number"""

    nhs_number = "1234567890"

    expected_error = "1234567890 is not a valid nhs number"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(orchestration_handler(event, ""))

    assert lambda_response.body["message"] == expected_error

    assert logger.was_value_logged("LAMBDA002", "reason", expected_error)


def test_orchestration_lambda_nhs_number_not_found(logger: LogHelper):
    """Test case for when PDS fails to find the provided nhs number"""

    nhs_number = "9449306621"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(orchestration_handler(event, ""))

    assert lambda_response.body["message"] == "PDS FHIR did not find matching record for nhs_number=9449306621"

    assert logger.was_value_logged("PDS002", "nhs_number", nhs_number)


def test_orchestration_lambda_error_in_pds(logger: LogHelper):
    """Test case for when PDS returns a status code that isn't 200 (found) or 400 (not found)"""

    # We use this nhs number as a flag for the mock to return a 500 status code
    nhs_number = "0000000000"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(orchestration_handler(event, ""))

    assert lambda_response.body["message"] == "PDS FHIR returned a non-200 status code with status_code=500"

    assert logger.was_value_logged("PDS003", "nhs_number", nhs_number)
    assert logger.was_value_logged("PDS003", "status_code", 500)


def test_orchestration_lambda_no_ods_on_record(logger: LogHelper):
    """Test case for when PDS fails to find the provided nhs number"""

    # This nhs number has no items in the general practitioner array
    # See tests/data/pds_responses/nhs_number_9449306613.json
    nhs_number = "9449306613"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(orchestration_handler(event, ""))

    assert lambda_response.body["message"] == "Pds found record for nhs_number=9449306613 but ODS code not present"

    assert logger.was_value_logged("PDS004", "nhs_number", nhs_number)
