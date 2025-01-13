import random
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from django.conf import settings
from decouple import config
from twilio.rest import Client

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    subject = "Your OTP for Verification"
    message = f"Your OTP is {otp}. It will expire in 10 minutes."
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [email])

def send_otp_sms(phone_number, otp):
    account_sid = config('TWILIO_ACCOUNT_SID')
    auth_token = config('TWILIO_ACCOUNT_TOKEN')
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f"Your OTP for password reset is {otp}. It is valid for 10 minutes.",
        from_="your_twilio_number",
        to=phone_number
    )
    return message.sid
