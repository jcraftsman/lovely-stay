import flask
import functions_framework


@functions_framework.http
def http_post_bookings(http_request: flask.Request):
    booking_request = parse(http_request)
    check_pricing(booking_request.agreed_pricing)
    verify_payment(booking_request.payment_method)
    booking_confirmed = book_rooms(booking_request)
    send_confirmation_email(booking_confirmed)
    return http_response(booking_confirmed)


def parse(request):
    return request.get_json()


def http_response(booking_confirmed):
    pass


def check_pricing(agreed_pricing):
    pass

def verify_payment(payment_method):
    pass


class BookingConfirmed:
    pass


def book_rooms(selected_rooms) -> BookingConfirmed:
    pass


def send_confirmation_email(main_guest):
    pass