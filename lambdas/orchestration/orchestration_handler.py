"""Lambda function linked to the /calculate api gateway route"""

import json
from http import HTTPStatus

from .lib.write_log import write_log


def orchestration_handler(event, _):
    """Entry point for events forwarded from the api gateway"""

    write_log("LAMBDA0001", {"event": event})

    parameters = event.get("queryStringParameters") or {}

    nhs_number = parameters.get("nhs_number")

    if not nhs_number:
        error = "nhs_number is required query string parameter"
        write_log("LAMBDA0002", {"reason": error})
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": json.dumps({"error": error}),
        }

    return {
        "statusCode": HTTPStatus.OK,
        "body": json.dumps({
            "nhs_number": nhs_number
        }),
    }
