def book_with_commitment_to_pay(booking_request):
    check_pricing(booking_request.agreed_pricing)
    verify_payment(booking_request.payment_method)
    booking_confirmed = book_rooms(booking_request)
    send_confirmation_email(booking_confirmed)
    return booking_confirmed


def create_booking(booking_request):
    booking = create_booking_from(booking_request)
    save(booking)
    return booking


def check_pricing(agreed_pricing):
    pass


def verify_payment(payment_method):
    pass


class BookingConfirmed:
    pass


def book_rooms(selected_rooms) -> BookingConfirmed:
    pass


def send_confirmation_email(booking_confirmed):
    pass
