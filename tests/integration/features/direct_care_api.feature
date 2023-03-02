@integration
Feature: Direct Care API

  @critical
  Scenario Outline: I can start a new game of Cookie Clicker
    When I request to start a new game with the name "<NAME>"
    Then a new game is started
    Examples:
      | NAME |
      | Bob  |
      | Sean |

  @minor
  Scenario: I cannot start a new game without a name
    When I request to start a new game with the name ""
    Then An error saying I need to include a name is displayed
