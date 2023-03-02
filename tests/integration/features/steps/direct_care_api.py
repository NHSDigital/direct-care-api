from behave import then, when

from tests.integration.methods import api_methods


@when("I request to start a new game with the name {}")
def start_new_game(context, name: str):
    api_methods.start_new_game(context=context, name=name)


@then("An error saying I need to include a name is displayed")
def no_player_name_error_is_displayed(context):
    api_methods.missing_player_name_error_is_displayed(context)


@then("a new game is started")
def a_new_game_is_started(context):
    api_methods.a_new_game_is_started(context)
