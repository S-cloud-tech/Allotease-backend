from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import BadHeaderError

def send_booking_email(to_email, seat_number):
    subject = "Your Seat Booking Confirmation"
    message = f"Thank you for booking! Your seat number is {seat_number}."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [to_email]

    try:
        send_mail(subject, message, from_email, recipient_list)
    except BadHeaderError:
        print("Invalid header found.")
    except Exception as e:
        print(f"Error sending email: {e}")
