from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from django.utils.timezone import now, timedelta
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

            # Generate and send OTP
            otp = generate_otp()
            user.otp = otp
            user.otp_created_at = now()
            user.save()

            send_otp_email(user.email, otp)

            return Response({
                "message": "User registered successfully. An OTP has been sent to your email for verification."
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
                "message": "Login successful."
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

    def post(self, request):
        serializer = serializers.VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = Account.objects.get(email=email)

            # Mark email as verified
            user.email_verified = True
            user.otp = None
            user.otp_created_at = None
            user.save()

            return Response({"message": "Email verified successfully."}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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

