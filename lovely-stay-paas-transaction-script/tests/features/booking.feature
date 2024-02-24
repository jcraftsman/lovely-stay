Feature: booking with commitment to pay
  As a future guest
  I want to book a hotel room
  So that I can have a lovely place to stay

  Scenario: confirming the booking of an available room
    Given a room "BF_PAR_701" was available starting from "2024-01-01" with pricing "MID_SEA_CAT1"
    And user's payment "CB_X01A" was authorized
    When the user books the room with a commitment to pay
      | room number | check-in   | check-out  | agreed pricing | payment method |
      | BF_PAR_701  | 2024-03-24 | 2024-03-31 | MID_SEA_CAT1   | CB_X01A        |
    Then his booking is confirmed

  Scenario: rejecting the booking of an already booked room
    Given a room "BF_PAR_701" was available starting from "2024-01-01" with pricing "MID_SEA_CAT1"
    And user's payment "CB_X01A" was authorized
    But the room was booked by someone else
      | room number | check-in   | check-out  | agreed pricing | payment method |
      | BF_PAR_701  | 2024-03-25 | 2024-03-28 | MID_SEA_CAT1   | VISA_YT12B     |
    When the user books the room with a commitment to pay
      | room number | check-in   | check-out  | agreed pricing | payment method |
      | BF_PAR_701  | 2024-03-24 | 2024-03-31 | MID_SEA_CAT1   | CB_X01A        |
    Then his booking is rejected