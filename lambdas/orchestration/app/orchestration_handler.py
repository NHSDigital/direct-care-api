"""Lambda function linked to the /calculate api gateway route"""

import json
from http import HTTPStatus
from uuid import uuid4

import dpath  # type: ignore
from nhs_number import is_valid  # type: ignore

from .lib.pds_fhir import lookup_nhs_number
from .lib.ssp_request import ssp_request
from .lib.write_log import write_log


def wrap_lambda_return(status, body):
    return {
        "statusCode": status,
        "body": json.dumps(body),
        "headers": {"test_header": "test_value"},
        "isBase64Encoded": False,
    }


class MissingAuditInfoException(ValueError):
    """Exception to raise when either user_id or user_org_code is missing"""


class LambdaHandler:
    """Wrapper for the lambda function in order to save audit info as class attributes"""

    transaction_id = None
    user_id = None
    user_org_code = None

    def set_audit_info(self, event):
        # Set a new transaction ID for each request that comes into that lambda
        self.transaction_id = uuid4()

        self.user_id = dpath.get(event, "headers/x-user-id")
        if not self.user_id:
            raise MissingAuditInfoException("User Id must be included in headers as x-user-id")

        self.user_org_code = dpath.get(event, "headers/x-user-org-code")
        if not self.user_org_code:
            raise MissingAuditInfoException(
                "User org code must be included in headers as x-user-org-code"
            )

    def write_log(self, log_ref, log_dict):
        """Wrapper for write log function inserting the audit data"""
        audit_dict = {
            "user_id": self.user_id,
            "user_org_code": self.user_org_code,
            "transaction_id": self.transaction_id,
        }
        write_log(log_ref, log_dict, audit_dict)

    def orchestration_handler(self, event):
        """Entry point for events forwarded from the api gateway"""

        try:
            self.set_audit_info(event)
        except MissingAuditInfoException as e:
            self.write_log("LAMBDA002", {"reason": str(e)})
            return wrap_lambda_return(HTTPStatus.BAD_REQUEST, {"record": None, "message": str(e)})

        self.write_log("LAMBDA001", {"event": event})

        parameters = event.get("queryStringParameters") or {}

        nhs_number = parameters.get("nhs_number")

        if not nhs_number:
            error = "nhs_number is required query string parameter"
            self.write_log("LAMBDA002", {"reason": error})
            return wrap_lambda_return(HTTPStatus.BAD_REQUEST, {"record": None, "message": error})

        if not is_valid(nhs_number):
            error = f"{nhs_number} is not a valid nhs number"
            self.write_log("LAMBDA002", {"reason": error})
            return wrap_lambda_return(HTTPStatus.BAD_REQUEST, {"record": None, "message": error})

        ods_code, error = lookup_nhs_number(nhs_number, self.write_log)

        if not ods_code:
            # Logging is done for this in the pds function
            return wrap_lambda_return(HTTPStatus.BAD_REQUEST, {"record": None, "message": error})

        org_fhir_endpoint, asid = (
            # pylint: disable=line-too-long
            "https://messagingportal.opentest.hscic.gov.uk:19192/B82617/STU3/1/gpconnect/structured/fhir/",
            "918999198738",
        )

        record, message = ssp_request(org_fhir_endpoint, asid, nhs_number, self.write_log)

        if not record:
            # Logging is done for this in the pds function
            return wrap_lambda_return(HTTPStatus.BAD_REQUEST, {"record": None, "message": message})

        return wrap_lambda_return(
            HTTPStatus.OK,
            {"record": record, "message": "success"},
        )


def main(event, _):
    """Instantiate class and call function"""
    return LambdaHandler().orchestration_handler(event)
