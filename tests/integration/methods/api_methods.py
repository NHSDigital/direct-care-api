import requests
from .asserter import wrapped_assert_that as assert_that


def start_new_game(context, name: str):
    body = f"name={name}"
    headers = {"content-type": "application/x-www-form-urlencoded"}
    context.response = requests.post(
        headers=headers, url=context.base_url + "/new_game", data=body
    )
    context.player_name = name


def missing_player_name_error_is_displayed(context):
    assert_that(requests.codes.bad, context.response.status_code, context=context)
    assert_that(expected="Player name must be supplied", actual=context.response.json(), context=context)


def a_new_game_is_started(context):
    context.expected = requests.codes.ok
    assert_that(actual=context.response.status_code, expected=requests.codes.ok, context=context)
