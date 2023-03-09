import requests
from assertpy import assert_that


def request_record(context, nhs_number: int):
    headers = {"content-type": "application/x-www-form-urlencoded"}
    context.response = requests.get(
        headers=headers, url=context.base_url + f"/record/structured?nhs_number={nhs_number}")
    context.nhs_number = nhs_number


def missing_player_name_error_is_displayed(context):
    assert_that(context.response.status_code).is_equal_to(requests.codes.bad)
    assert_that(context.response.json()).is_equal_to("Player name must be supplied")


def a_new_game_is_started(context):
    context.expected = requests.codes.ok
    assert_that(context.response.status_code).is_equal_to(requests.codes.ok)
