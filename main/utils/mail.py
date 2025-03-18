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

def send_refund_email(user_email, subject, message):
    """Send email notification for refund status"""
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [user_email],
        fail_silently=False,
    )

def generate_shareable_links(ticket):
    base_url = "http://127.0.0.1:8000/main/tickets" #Change in Production  
    return f"{base_url}/{ticket.id}/"