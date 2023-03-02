"""Lambda function linked to the /calculate api gateway route"""

import json
from http import HTTPStatus


def orchestration_handler(event, _):
    """Entry point for events forwarded from the api gateway"""

    parameters = event.get("queryStringParameters") or {}

    nhs_number = parameters.get("nhs_number")

    if not nhs_number:
        return {
            "statusCode": HTTPStatus.BAD_REQUEST,
            "body": json.dumps({"error": "nhs_number is required query string parameter"}),
        }

    return {
        "statusCode": HTTPStatus.OK,
        "body": json.dumps({
            "nhs_number": nhs_number
        }),
    }
