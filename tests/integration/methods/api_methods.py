import requests
from assertpy import assert_that


def start_new_game(context, name: str):
    body = f"name={name}"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    context.response = requests.post(
        headers=headers, url=context.base_url + "/new_game", data=body
    )
    context.player_name = name


def missing_player_name_error_is_displayed(context):
    assert_that(context.response.status_code).is_equal_to(requests.codes.bad)
    assert_that(context.response.json()).is_equal_to("Player name must be supplied")


def a_new_game_is_started(context):
    context.expected = requests.codes.ok
    assert_that(context.response.status_code).is_equal_to(requests.codes.ok)
