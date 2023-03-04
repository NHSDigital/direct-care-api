"""Lambda function linked to the /calculate api gateway route"""

import json
from http import HTTPStatus

from nhs_number import is_valid

from .lib.pds_fhir import lookup_nhs_number
from .lib.write_log import write_log


def wrap_lambda_return(status, body):
    return {
        "statusCode": status,
        "body": json.dumps(body),
        "headers": {"test_header": "test_value"},
        "isBase64Encoded": False,
    }


def orchestration_handler(event, _):
    """Entry point for events forwarded from the api gateway"""

    write_log("LAMBDA001", {"event": event})

    parameters = event.get("queryStringParameters") or {}

    nhs_number = parameters.get("nhs_number")

    if not nhs_number:
        error = "nhs_number is required query string parameter"
        write_log("LAMBDA002", {"reason": error})
        return wrap_lambda_return(
            HTTPStatus.BAD_REQUEST, {"record": None, "message": error}
        )

    if not is_valid(nhs_number):
        error = f"{nhs_number} is not a valid nhs number"
        write_log("LAMBDA002", {"reason": error})
        return wrap_lambda_return(
            HTTPStatus.BAD_REQUEST, {"record": None, "message": error}
        )

    ods_code, error = lookup_nhs_number(nhs_number)

    if not ods_code:
        # Logging is done for this in the pds function
        return wrap_lambda_return(
            HTTPStatus.BAD_REQUEST, {"record": None, "message": error}
        )

    return wrap_lambda_return(
        HTTPStatus.OK,
        {"record": ods_code, "message": "success"},
    )
