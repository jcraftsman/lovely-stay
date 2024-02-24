from dataclasses import dataclass

from behave import *
from behave.runner import Context

from lovely_stay_paas_transaction_script.booking_transaction import book_with_commitment_to_pay, BookingRequest, \
    StayPeriod, PaymentMethod, RoomId, PricingId


def add_room(room_id, param):
    pass


def publish_pricing(room_id, pricing_id, availability_start_date):
    pass


@dataclass
class RoomDescription:
    guest_capacity: int
    bed_count: int
    floor: int
    description: str


@given('a room "{room_id}" was available starting from "{availability_start_date}" with pricing "{pricing_id}"')
def step_impl(context: Context, room_id: RoomId, availability_start_date: str, pricing_id: PricingId):
    add_room(room_id, RoomDescription(3, 2, 7, ""))
    publish_pricing(room_id, pricing_id, availability_start_date)


@step('user\'s payment "{payment_intent_token}" was authorized')
def step_impl(context: Context, payment_intent_token: str):
    pass


@when("the user books the room with a commitment to pay")
def step_impl(context: Context):
    execute_booking_request_from(context)


@then("his booking is confirmed")
def step_impl(context: Context):
    assert not context.failed


@step("the room was booked by someone else")
def step_impl(context: Context):
    execute_booking_request_from(context)


@then("his booking is rejected")
def step_impl(context: Context):
    assert context.failed


def execute_booking_request_from(context: Context):
    first_booking_request = context.table[0]
    booking_request = BookingRequest(agreed_pricing=first_booking_request["agreed pricing"],
                                     payment_method=PaymentMethod(first_booking_request["payment method"]),
                                     selected_rooms=["room number"],
                                     stay_period=StayPeriod.of(first_booking_request["check-in"],
                                                               first_booking_request["check-out"]),
                                     main_guest="user1")
    book_with_commitment_to_pay(booking_request)
