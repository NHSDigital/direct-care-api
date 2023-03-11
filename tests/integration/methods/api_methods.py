import logging
import jsonschema
import requests
from assertpy import assert_that
from jsonschema import validate


def log_api_information(context):
    logging.info("REQUEST")
    logging.info("Headers: %s ", context.response.request.headers)
    logging.info("Method: %s ", context.response.request.method)
    logging.info("URL: %s ", context.response.request.url)
    logging.info("Body: %s ", context.response.request.body)
    logging.info("RESPONSE")
    logging.info("Status Code: %s ", context.response.status_code)
    logging.info("Headers: %s ", context.response.headers)
    logging.info("Body: %s ", context.response.content)


def get_expected_schema():
    record_schema = {
        "record": "object",
        'message': {"type": "string"},
        'user_id': {"type": "string"},
        'user_org_code': {"type": "string"},
        'transaction_id': {"type": "string"}
    }
    return record_schema


def get_default_headers():
    return {"x-user-id": "AutoTests",
            "x-user-org-code": "Auto001"}


def is_validate_json(json_data):
    try:
        validate(instance=json_data, schema=get_expected_schema())
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True


def request_record(context, nhs_number: int):
    headers = get_default_headers()
    context.response = requests.get(
        headers=headers, url=context.base_url + f"/record/structured?nhs_number={nhs_number}")
    context.nhs_number = nhs_number
    log_api_information(context)


def the_expected_response_code_is_returned(context, expected_response_code: requests.codes):
    assert_that(context.response.status_code).is_equal_to(expected_response_code)


def a_structured_record_is_returned(context):
    response = context.response.json()
    assert_that(is_validate_json(response)).is_true()
    assert_that(response["record"]).is_not_none()
    assert_that(response["message"]).is_equal_to("success")
    assert_that(response["user_id"]).is_equal_to("AutoTests")
    assert_that(response["user_org_code"]).is_equal_to("Auto001")
    assert_that(response["transaction_id"]).is_not_none()
