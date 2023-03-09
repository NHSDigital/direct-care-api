from behave import then, when

from tests.integration.methods import api_methods


@when("I request my care record with the NHS Number {}")
def request_record_with_nhs_number(context, nhs_number: int):
    api_methods.request_record(context=context, nhs_number=nhs_number)


@then("my record is returned")
def my_record_is_returned(context):
    api_methods.a_new_game_is_started(context)


@then("An error saying I need to include a name is displayed")
def no_player_name_error_is_displayed(context):
    api_methods.missing_player_name_error_is_displayed(context)
