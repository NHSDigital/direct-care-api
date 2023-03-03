"""Lambda function linked to the /calculate api gateway route"""

import json
from http import HTTPStatus

from .lib.pds_fhir import lookup_nhs_number
from .lib.write_log import write_log


def orchestration_handler(event, _):
    """Entry point for events forwarded from the api gateway"""

    write_log("LAMBDA001", {"event": event})

    parameters = event.get("queryStringParameters") or {}

    nhs_number = parameters.get("nhs_number")

    if not nhs_number:
        error = "nhs_number is required query string parameter"
        write_log("LAMBDA002", {"reason": error})
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": json.dumps({"error": error}),
            "headers": {"test_header": "test_value"},
            "isBase64Encoded": False
        }

    pds_status_code, pds_body = lookup_nhs_number(nhs_number)

    return {
        "statusCode": HTTPStatus.OK,
        "body": json.dumps({
            "nhs_number": nhs_number,
            "pds_status_code": pds_status_code,
            "pds_record": pds_body,
        }),
        "headers": {"test_header": "test_value"},
        "isBase64Encoded": False
    }
