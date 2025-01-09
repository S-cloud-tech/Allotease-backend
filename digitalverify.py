from django.contrib.auth.models import User
from django.db import models
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django_otp.oath import TOTP
from django_otp.util import random_hex
from datetime import timedelta
import pyotp
import requests

# Models
class MFADevice(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mfa_device')
    secret_key = models.CharField(max_length=32, default=random_hex)
    last_verified = models.DateTimeField(null=True, blank=True)

class DigitalIdentityVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='digital_identity')
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(upload_to='verification_documents/')
    verification_date = models.DateTimeField(null=True, blank=True)

# Utilities
def generate_backup_codes():
    return [get_random_string(length=10) for _ in range(5)]

def send_email_otp(user, otp):
    send_mail(
        subject="Your OTP Code",
        message=f"Your One-Time Password is: {otp}",
        from_email="no-reply@example.com",
        recipient_list=[user.email],
    )

def verify_document_with_third_party(document_path):
    # Mock third-party document verification
    # Replace with actual API call to a document verification provider
    response = requests.post("https://thirdparty.verification.api/verify", files={"document": open(document_path, "rb")})
    return response.status_code == 200

# Views
class SetupMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Create or retrieve the MFA device for the user
        mfa_device, created = MFADevice.objects.get_or_create(user=user)

        # Generate a QR code URL using pyotp
        totp = pyotp.TOTP(mfa_device.secret_key)
        provisioning_uri = totp.provisioning_uri(
            name=user.username, issuer_name="Django Ticket API"
        )

        # Optionally, generate backup codes
        backup_codes = generate_backup_codes()

        return Response({
            "provisioning_uri": provisioning_uri,
            "backup_codes": backup_codes,
        })

class VerifyMFAView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp = request.data.get("otp")

        if not otp:
            raise ValidationError("OTP is required.")

        mfa_device = get_object_or_404(MFADevice, user=user)
        totp = pyotp.TOTP(mfa_device.secret_key)

        # Verify OTP
        if totp.verify(otp):
            mfa_device.last_verified = now()
            mfa_device.save()
            return Response({"detail": "MFA verification successful."})

        raise ValidationError("Invalid OTP.")

class GenerateEmailOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp = default_token_generator.make_token(user)

        send_email_otp(user, otp)
        return Response({"detail": "Email OTP sent."})

class VerifyEmailOTPView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        otp = request.data.get("otp")

        if not otp:
            raise ValidationError("OTP is required.")

        if default_token_generator.check_token(user, otp):
            return Response({"detail": "Email OTP verification successful."})

        raise ValidationError("Invalid OTP.")

class UploadVerificationDocumentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        file = request.FILES.get("document")

        if not file:
            raise ValidationError("Verification document is required.")

        digital_identity, created = DigitalIdentityVerification.objects.get_or_create(user=user)
        digital_identity.verification_document = file
        digital_identity.save()

        # Simulate verification with a third-party service
        document_path = digital_identity.verification_document.path
        is_verified = verify_document_with_third_party(document_path)

        if is_verified:
            digital_identity.is_verified = True
            digital_identity.verification_date = now()
            digital_identity.save()
            return Response({"detail": "Document verification successful."})

        return Response({"detail": "Document verification failed."}, status=400)

# Middleware or Authentication Classes
# You can extend the Django or DRF authentication classes to enforce MFA and digital identity checks during login or sensitive actions.
