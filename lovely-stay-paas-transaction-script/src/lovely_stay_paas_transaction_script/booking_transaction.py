from dataclasses import dataclass
from datetime import datetime
from typing import TypeAlias

PricingId: TypeAlias = str
RoomId: TypeAlias = str


@dataclass
class PaymentMethod:
    id: str


class StayPeriod:
    checkin_date: datetime
    checkout_date: datetime

    @classmethod
    def of(cls, str_checkin: str, str_checkout: str) -> "StayPeriod":
        pass


UserId: TypeAlias = str


@dataclass
class BookingRequest:
    agreed_pricing: PricingId
    payment_method: PaymentMethod
    selected_rooms: list[RoomId]
    stay_period: StayPeriod
    main_guest: UserId


class BookingConfirmed:
    pass


def book_with_commitment_to_pay(booking_request: BookingRequest) -> BookingConfirmed:
    check_pricing(booking_request.agreed_pricing)
    verify_payment(booking_request.payment_method)
    booking_confirmed = book_rooms(booking_request)
    send_confirmation_email(booking_confirmed)
    return booking_confirmed


def check_pricing(agreed_pricing):
    pass


def verify_payment(payment_method):
    pass


class BookingConfirmed:
    pass


def book_rooms(selected_rooms: list[RoomId]) -> BookingConfirmed:
    pass

def send_confirmation_email(booking_confirmed):
    pass
