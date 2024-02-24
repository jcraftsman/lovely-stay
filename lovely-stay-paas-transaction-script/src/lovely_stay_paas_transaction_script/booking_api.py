from fastapi import FastAPI

from lovely_stay_paas_transaction_script.booking_transaction import book_with_commitment_to_pay, BookingRequest

app = FastAPI()


@app.post("/bookings")
def http_post_bookings(http_request):
    booking_request = parse(http_request)
    booking_confirmed = book_with_commitment_to_pay(booking_request)
    return http_response(booking_confirmed)


def parse(http_request) -> BookingRequest:
    pass


def http_response(booking_confirmed):
    pass
