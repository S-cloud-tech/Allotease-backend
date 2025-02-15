from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from django.utils.timezone import now
from django.core.cache import cache
from . import serializers
from .models import Account
from .utility import generate_otp, send_otp_email, send_otp_sms

# Register Users and Sending OTP to email
class RegisterView(generics.GenericAPIView):
    serializer_class = serializers.RegisterSerializer
    
    def  post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        if serializer.is_valid():
            # Create the user
            user = serializer.save()

            user_data = serializer.data
            user = Account.objects.get(email=user_data['email'])
            token = RefreshToken.for_user(user)

            return Response({
                "message": "User registered successfully. An OTP has been sent to your email for verification." # Remove in production
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Login Users
class LoginView(generics.GenericAPIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request):
        serializer = serializers.LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Generate or retrieve the token for the user
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                "token": token.key,
                "message": "Login successful." # Remove in production
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Sending OTP to user's email   
class SendOTPView(generics.GenericAPIView):
    serializer_class = serializers.SendOTPSerializer

    def post(self, request):
        serializer = serializers.SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = Account.objects.get(email=email)

            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = now()
            user.save()

            send_otp_email(email, otp)
            return Response({"message": "OTP sent to your email."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Verifying the sent OTP
class VerifyOTPView(generics.GenericAPIView):
    serializer_class = serializers.VerifyOTPSerializer
    OTP_RETRY_LIMIT = 5  # Maximum allowed attempts
    OTP_RETRY_TIMEOUT = 300  # Timeout in seconds (5 minutes)

    def post(self, request):
        email = request.data.get("email", None)
        phone_number = request.data.get("phone_number", None)

        # Create a unique cache key based on the identifier
        identifier = email if email else phone_number
        if not identifier:
            return Response({"error": "Email or phone number is required."}, status=status.HTTP_400_BAD_REQUEST)

        cache_key = f"otp_attempts_{identifier}"

        # Get the current number of attempts
        attempts = cache.get(cache_key, 0)

        # Check if the user has exceeded the retry limit
        if attempts >= self.OTP_RETRY_LIMIT:
            return Response(
                {"error": "Too many invalid attempts. Please try again later."},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Validate OTP
        serializer = serializers.VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            if "email" in request.data:
                user.email_verified = True
            if "phone_number" in request.data:
                user.phone_verified = True

            user.otp = None  # Clear OTP after successful verification
            user.otp_created_at = None
            user.save()

            # Clear cache on successful verification
            cache.delete(cache_key)

            return Response({"message": "Verification successful."}, status=status.HTTP_200_OK)
        else:
            # Increment the number of attempts
            cache.set(cache_key, attempts + 1, self.OTP_RETRY_TIMEOUT)
            return Response(
                {"error": "Invalid OTP. Please try again."},
                status=status.HTTP_400_BAD_REQUEST
            )
     
# Request for password reset
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = serializers.PasswordResetRequestSerializer

    def post(self, request):
        serializer = serializers.PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email_or_phone = serializer.validated_data['email_or_phone']

            if '@' in email_or_phone:  # Email
                user = Account.objects.get(email=email_or_phone)
                send_otp_email(user.email, user.otp)
            else:  # Phone
                user = Account.objects.get(phone_number=email_or_phone)
                send_otp_sms(user.phone_number, user.otp)

            # Generate and save OTP
            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = now()
            user.save()

            return Response({"message": "OTP sent successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Reset Password
class PasswordResetView(generics.GenericAPIView):
    serializer_class = serializers.PasswordResetSerializer

    def post(self, request):
        serializer = serializers.PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AccountProfileView(generics.RetrieveAPIView):
    serializer_class = serializers.AccountSerializer
    permission_classes = []

    def get(self, request):
        """Retrieve the authenticated user's profile."""
        user = request.user
        serializer = serializers.AccountSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        """Update the authenticated user's profile."""
        user = request.user
        serializer = serializers.UpdateAccountProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        """Delete the authenticated user's profile."""
        user = request.user
        user.delete()
        return Response({"message": "User profile deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


