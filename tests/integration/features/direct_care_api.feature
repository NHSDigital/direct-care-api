@integration
Feature: Requesting Summary Care Records

  @critical
  Scenario: I can request a care record using a valid NHS number
    When I request my care record with the NHS Number 9690937278
    Then the correct record is returned