@integration
Feature: Requesting Summary Care Records

  @critical @smoke
  Scenario: I can request a care record using a valid NHS number
    When I request my care record with the NHS Number 9690937278
    Then the correct record is returned

  Scenario Outline: I cannot request a care record using an invalid NHS number
    When I request my care record with the NHS Number <nhs_number>
    Then an error is displayed to say the NHS number is invalid
    Examples:
      | nhs_number |
      | INVALID    |
      | 123        |
      | 1234567890 |

  Scenario: I cannot request a care record without an NHS number
    When I request my care record without an NHS Number
    Then an error is displayed to say the NHS number is required
