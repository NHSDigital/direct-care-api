@integration
Feature: Direct Care API

  @critical
  Scenario Outline: I can request my care record
    When I request my care record with the NHS Number "<NHS_NUMBER>"
    Then my record is returned
    Examples:
      | NHS_NUMBER |
      | Bob  |
      | Sean |

  @minor
  Scenario: I cannot start a new game without a name
    When I request to start a new game with the name ""
    Then An error saying I need to include a name is displayed
