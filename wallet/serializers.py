from django.db.models import Sum
from django.conf import settings
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from .models import Virtual_accounts, Transactions
import requests
from accounts.models import Account

class WalletSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    def get_balance(self, obj):
        bal = Transactions.objects.filter(
            wallet=obj, status="success").aaggregate(Sum('amount'))['amount_sum']
        return bal
    
    class Meta:
        model = Virtual_accounts
        fields = ['id', 'currency', 'balance']

def is_amount(value):
    if value <= 0:
        raise serializers.ValidationError({"detail": "Invalid Amount"})


class DepositSerializer(serializers.Serializer):
    amount = serializers.IntegerField(validators=[is_amount])
    email = serializers.EmailField()

    def validate_email(self, value):
        if Account.objects.filter(email=value).exists():
            return value
        raise serializers.ValidationError({"detail": "Email not found"})

    def save(self):
        user = self.context['request'].user
        wallet = Virtual_accounts.objects.get(user=user)
        data = self.validate_data
        url = 'https://api.paystack.co/transaction/initialize'
        headers = {
            {"authorization": f"Bearer{settings.PAYSTACK_TEST_SECRET_KEY}"}
            
        }

