import json
from uuid import uuid4


def parse_response(lambda_response):
    class LambdaResponse:
        """
        Wrapper for the dict response that comes back from lambda handler
        Makes it easier to access dict items as properties
        """

        @property
        def status_code(self):
            return lambda_response.get("statusCode")

        @property
        def body(self):
            return json.loads(lambda_response.get("body"))

    return LambdaResponse()


def mock_orchestration_event(nhs_number, user_org_code=None, user_id=None):
    return {
        "body": None,
        "queryStringParameters": {"nhs_number": nhs_number},
        "headers": {
            "content-type": "application/json",
            "Host": "https://aws.com/gaetway_id/r9srwxlz3d",
            "x-user-org-code": "A10456" if user_org_code is None else user_org_code,
            "x-user-id": uuid4() if user_id is None else user_id,
        },
    }
