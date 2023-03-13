import requests
from behave import then, when

from tests.integration.methods import api_methods


@when("I request my care record with the NHS Number {nhs_number}")
def request_record_with_nhs_number(context, nhs_number):
    context.nhs_number = nhs_number
    api_methods.request_record(context=context, nhs_number=nhs_number)


@when("I request my care record without an NHS Number")
def step_impl(context):
    api_methods.request_record(context=context)


@then("the correct record is returned")
def the_correct_record_is_returned(context):
    api_methods.the_expected_response_code_is_returned(context, requests.codes.ok)
    api_methods.a_structured_record_is_returned(context)


@then("an error is displayed to say the NHS number is invalid")
def nhs_number_invalid_error_message_displayed(context):
    api_methods.the_expected_response_code_is_returned(context, requests.codes.bad)
    api_methods.error_is_returned(context, context.nhs_number + " is not a valid nhs number")


@then("an error is displayed to say the NHS number is required")
def nhs_number_required_error_message_displayed(context):
    api_methods.the_expected_response_code_is_returned(context, requests.codes.bad)
    api_methods.error_is_returned(context, "nhs_number is required query string parameter")
