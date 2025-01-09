from rest_framework import serializers
from . models import Account

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=20, min_length=8, write_only=True)

    class Meta:
        model = Account
        fields = ['email', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '') 
        return attrs
    
    def create(self, validated_data):
        return Account.objects.create_user(**validated_data)

