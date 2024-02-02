from fastapi import FastAPI

from lovely_stay_paas_transaction_script.booking_transaction import book_with_commitment_to_pay

app = FastAPI()


@app.post("/bookings")
def http_post_bookings(http_request):
    booking_request = parse(http_request)
    booking_confirmed = book_with_commitment_to_pay(booking_request)
    return http_response(booking_confirmed)


@app.post("/gateway/mails/booking-confirmation/{booking_id}")
def http_post_mails_booking_confirmation(booking_id):
    booking = fetch_booking(booking_id)
    confirmation_email = build_mail(booking)
    send_email(mail)


def parse(http_request):
    pass


def http_response(booking_confirmed):
    pass
