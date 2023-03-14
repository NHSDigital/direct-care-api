import requests
from behave import then, when

from tests.integration.methods import api_methods


@when("I request my care record with the NHS Number {nhs_number:d}")
def request_record_with_nhs_number(context, nhs_number: int):
    api_methods.request_record(context=context, nhs_number=nhs_number)


@then("the correct record is returned")
def the_correct_record_is_returned(context):
    api_methods.the_expected_response_code_is_returned(context, requests.codes.ok)
    api_methods.a_structured_record_is_returned(context)
