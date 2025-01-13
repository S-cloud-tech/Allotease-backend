from rest_framework import serializers
from django.contrib.auth import authenticate
from django.utils.timezone import now, timedelta
from . models import Account

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type' : 'password'}, write_only=True)

    class Meta:
        model = Account
        fields = [
            'email','password', 'password2',
            ]
        extra_kwarg = {
            'password' : {'write_only' : True}
        }

    def validate(self, attrs):
        email = attrs.get('email', '') 
        return attrs

    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)
    
    def save(self):
        password = self.validated_data['password']    
        password2 = self.validated_data['password2']
        
        #Add validations before saving

        if password != password2:
            raise serializers.ValidationError({'password' : 'Passwords do not match.'})  #Make sure that passwords match

        account = Account (
            # phone=self.validated_data['phone'],
            # fullname = self.validated_data['fullname'],
            # first_name = self.validated_data['first_name'],
            # last_name = self.validated_data['last_name'],
            email = self.validated_data['email'],
        )
        
        account.set_password(password)
        account.save()
        return account

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = authenticate(username=email, password=password)
        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.email_verified:
            raise serializers.ValidationError("Email is not verified. Please verify your email before logging in.")

        data['user'] = user
        return data

class PasswordResetRequestSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()

    def validate_email_or_phone(self, value):
        if '@' in value:  # Assume it's an email
            if not Account.objects.filter(email=value).exists():
                raise serializers.ValidationError("No user is associated with this email.")
        else:  # Assume it's a phone number
            if not Account.objects.filter(phone_number=value).exists():
                raise serializers.ValidationError("No user is associated with this phone number.")
        return value

class PasswordResetSerializer(serializers.Serializer):
    email_or_phone = serializers.CharField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        email_or_phone = data.get('email_or_phone')
        otp = data.get('otp')

        if '@' in email_or_phone:  # Handle email
            user = Account.objects.filter(email=email_or_phone).first()
        else:  # Handle phone
            user = Account.objects.filter(phone_number=email_or_phone).first()

        if not user:
            raise serializers.ValidationError("User not found.")

        if user.otp != otp:
            raise serializers.ValidationError("Invalid OTP.")

        # Check if OTP has expired
        if user.otp_created_at and (now() - user.otp_created_at) > timedelta(minutes=10):
            raise serializers.ValidationError("OTP has expired.")

        data['user'] = user
        return data

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.otp = None  # Clear the OTP after successful password reset
        user.otp_created_at = None
        user.save()
        return user


class AccountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Account
        fields = [
            'id','first_name', 'last_name', 'email',
            'phone','profile_image',
        ]

    # This is to update user details 
    def update(self, instance,validated_data):

        if self.validated_data.get('first_name'):
            instance.first_name=self.validated_data['first_name']
        if self.validated_data.get('last_name'):
            instance.last_name=self.validated_data['last_name']
        if self.validated_data.get('phone'):
            instance.phone=self.validated_data['phone']
        if self.validated_data.get('email'):
            instance.email=self.validated_data['email']
        if self.validated_data.get('profile_image'):
            instance.profile_image = self.validated_data['profile_image']
        
        # Save the instance 
        instance.save()
        return instance


class SendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = Account.objects.get(email=value)
        except Account.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        return value


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = Account.objects.get(email=data['email'])
        except Account.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")

        if user.otp != data['otp']:
            raise serializers.ValidationError("Invalid OTP.")
        
        if user.otp_created_at and (now() - user.otp_created_at) > timedelta(minutes=10):
            raise serializers.ValidationError("OTP has expired.")

        return data
