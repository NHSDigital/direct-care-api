from unittest.mock import Mock, patch
from uuid import uuid4

from ...app.orchestration_handler import main
from ..utils.log_helper import LogHelper
from ..utils.mock_post_request import MockPostRequest
from ..utils.test_utils import mock_orchestration_event, parse_response


def test_orchestration_lambda_success(logger: LogHelper):
    nhs_number = "9690937278"
    user_id = "USER1234"
    user_org_code = "ODS1234"
    transaction_id = uuid4()

    event = mock_orchestration_event(nhs_number, user_id=user_id, user_org_code=user_org_code)

    # Patch UUID4 so that we can insert our own uuid
    with patch("lambdas.orchestration.app.orchestration_handler.uuid4") as mock_uuid:
        mock_uuid.return_value = transaction_id
        lambda_response = parse_response(main(event, ""))

    assert lambda_response.status_code == 200

    # Check the record ID returned matches what we expected from the mock SSP return
    assert lambda_response.body["record"]["id"] == "71f48f67-8055-4cbc-9a30-ecba6915a0d2"

    assert logger.was_value_logged("PDS001", "nhs_number", nhs_number)

    assert logger.was_logged("LAMBDA001")
    assert logger.was_logged("SSP001")
    assert logger.was_logged("SSP002")

    # Check audit logs were populated correctly
    assert logger.was_value_logged("LAMBDA001", "userId", user_id)
    assert logger.was_value_logged("LAMBDA001", "userOrgCode", user_org_code)
    assert logger.was_value_logged("LAMBDA001", "transactionId", transaction_id)


def test_orchestration_missing_user_id(logger: LogHelper):
    nhs_number = "9690937278"
    user_id = ""
    user_org_code = "ODS1234"

    event = mock_orchestration_event(nhs_number, user_id=user_id, user_org_code=user_org_code)

    lambda_response = parse_response(main(event, ""))

    assert lambda_response.status_code == 400

    assert lambda_response.body["message"] == "User Id must be included in headers as x-user-id"

    assert logger.was_value_logged("LAMBDA002", "reason", "")


def test_orchestration_missing_user_org_code(logger: LogHelper):
    nhs_number = "9690937278"
    user_id = "USER1234"
    user_org_code = ""

    event = mock_orchestration_event(nhs_number, user_id=user_id, user_org_code=user_org_code)

    lambda_response = parse_response(main(event, ""))

    assert lambda_response.status_code == 400

    assert (
        lambda_response.body["message"]
        == "User org code must be included in headers as x-user-org-code"
    )

    assert logger.was_value_logged("LAMBDA002", "reason", "")


def test_orchestration_lambda_no_nhs_number_provided(logger: LogHelper):
    nhs_number = None

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(main(event, ""))

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

    lambda_response = parse_response(main(event, ""))

    assert lambda_response.body["message"] == expected_error

    assert logger.was_value_logged("LAMBDA002", "reason", expected_error)


def test_orchestration_lambda_nhs_number_not_found(logger: LogHelper):
    """Test case for when PDS fails to find the provided nhs number"""

    nhs_number = "9449306621"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(main(event, ""))

    assert (
        lambda_response.body["message"]
        == "PDS FHIR did not find matching record for nhs_number=9449306621"
    )

    assert logger.was_value_logged("PDS002", "nhs_number", nhs_number)


def test_orchestration_lambda_error_in_pds(logger: LogHelper):
    """Test case for when PDS returns a status code that isn't 200 (found) or 400 (not found)"""

    # We use this nhs number as a flag for the mock to return a 500 status code
    nhs_number = "0000000000"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(main(event, ""))

    assert lambda_response.body["message"] == (
        "PDS FHIR returned a non-200 status code with status_code=500"
        " error=Unknown error - No diagnostics available"
    )

    assert logger.was_value_logged("PDS003", "nhs_number", nhs_number)
    assert logger.was_value_logged("PDS003", "status_code", 500)


def test_orchestration_lambda_no_ods_on_record(logger: LogHelper):
    # This nhs number has no items in the general practitioner array
    # See tests/data/pds_responses/nhs_number_9449306613.json
    nhs_number = "9449306613"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(main(event, ""))

    assert (
        lambda_response.body["message"]
        == "Pds found record for nhs_number=9449306613 but ODS code not present"
    )

    assert logger.was_value_logged("PDS004", "nhs_number", nhs_number)


def test_orchestration_lambda_no_match_on_ssp(logger: LogHelper):
    """Test case for when PDS finds a match but SSP fails to find the provided nhs number"""

    nhs_number = "9999999999"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(main(event, ""))

    assert (
        lambda_response.body["message"] == "SSP failed to find patient with nhs_number=9999999999"
    )

    assert logger.was_value_logged("SSP004", "nhs_number", nhs_number)


def test_orchestration_lambda_error_on_ssp(logger: LogHelper):
    """Test case for when PDS finds a match but SSP returns other non-200 status"""

    nhs_number = "1111111111"

    event = mock_orchestration_event(nhs_number)

    lambda_response = parse_response(main(event, ""))

    assert lambda_response.body["message"] == "SSP request returned non-200 status_code=500"

    assert logger.was_value_logged("SSP005", "status_code", 500)


def test_orchestration_exception_in_on_ssp(logger: LogHelper):
    nhs_number = "1111111111"

    event = mock_orchestration_event(nhs_number)

    # Re-patch the make request function so that it throws an error
    # The first side effect needs to remain as MockPostRequest as the first time requests.post is
    # called is on the oauth endpoint for the PDS request
    # Patch the second time it's called to throw the exception by passing a list to side_effect
    with patch(
        "lambdas.orchestration.app.lib.make_request.requests.post",
        Mock(side_effect=[MockPostRequest(), Exception("Boom!")]),
    ):
        lambda_response = parse_response(main(event, ""))

    assert lambda_response.body["message"] == "Exception in SSP request with error=Boom!"

    assert logger.was_value_logged("SSP003", "error", "Boom!")
