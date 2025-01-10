from rest_framework import serializers
from django.utils.timezone import now, timedelta
from . models import Account

class RegisterSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type' : 'password'}, write_only=True)
    # firstname = serializers.CharField(required=True)

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

class AccountSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Account
        fields = [
            'id','fullname', 'email',
            'phone','profile_image',
        ]

    # This is to update user details 
    def update(self, instance,validated_data):

        if self.validated_data.get('fullname'):
            instance.fullname=self.validated_data['fullname']
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
        
        if user.otp_created_at and user.otp_created_at + timedelta(minutes=10) < now():
            raise serializers.ValidationError("OTP has expired.")

        return data
