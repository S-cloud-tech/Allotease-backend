from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.timezone import now, timedelta
from . import serializers
from .models import Account
from .utility import generate_otp, send_otp_email

# Create your views here.
class RegisterView(generics.GenericAPIView):
    serializer_class = serializers.RegisterSerializer
    
    def  post(self, request):
        user = request.data
        serializers = self.serializer_class(data=user)
        serializers.is_valid(raise_exception=True)
        serializers. save()

        user_data = serializers.data
        user = Account.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user)

        return Response(user_data, status=status.HTTP_201_CREATED)
    
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