from django.db import models
from django.utils.timezone import now
from django.conf import settings
from paystackapi.transaction import Transaction
from main.utils.mail import send_refund_email
from user.models import Merchant
from .utils.currency_map import COUNTRY_TO_CURRENCY
from .utils.kuda import Kuda_model
import uuid
import secrets

class Virtual_account(models.Model):
    account_name =  models.CharField(max_length=200,null=True)
    account_number =  models.CharField(max_length=200,null=True,unique=True)
    bank_name =  models.CharField(max_length=200,null=True)
    bank_slug =  models.CharField(max_length=200,null=True)
    merchant = models.OneToOneField(Merchant, on_delete=models.CASCADE, null=True, related_name='virtual_account')
    currency = models.CharField(max_length=3, default='NGN', blank=True)
    status =  models.BooleanField(default=False)
    enabled =  models.BooleanField(default=False)
    total = models.PositiveIntegerField(default=0,null=True)
    amount_owed = models.PositiveIntegerField(default=0,null=True)
    withdrawable_balance = models.PositiveIntegerField(null=True)
    ledger_balance = models.PositiveIntegerField(null=True)
    date_created =models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self) -> str:
        return f'{self.account_name} : {self.account_number}'
    
    def save(self, *args, **kwargs):
        if not self.currency and self.merchant and self.merchant.country:
            country_code = self.merchant.country.code  # e.g., 'US'
            self.currency = COUNTRY_TO_CURRENCY.get(country_code, 'USD')  # Default fallback
        super().save(*args, **kwargs)

    def get_virtual_account(self):
        kuda = Kuda_model()
        status,data = kuda.get_virtual_account(self.ref)
        if status == True:
            info = data['Data']['Account']
            self.account_number = info['AccountNumber']
            self.account_name = info['AccountName']
            self.ref = info['TrackingReference']
        self.save()
        return status

    def disable_virtual_account(self):
        kuda = Kuda_model()
        status,data = kuda.disable_virtual_account(self.ref)
        if status == True:
            self.enabled = False
            self.save()
        return status

    def enable_virtual_account(self):
        kuda = Kuda_model()
        status,data = kuda.enable_virtual_account(self.ref)
        if status == True:
            self.enabled = True
            self.save()
        return status

    def get_virtual_account_balance(self):
        kuda = Kuda_model()
        status,data = kuda.get_virtual_account_balance(self.ref)
        self.status = status
        print(data)
        if status == True:
            info = data['Data']
            self.total = info['AvailableBalance']
            self.withdrawable_balance = info['WithdrawableBalance']
            self.ledger_balance = info['LedgerBalance']
        self.save()
        return status,self.total

class Transaction(models.Model):

    CREDIT = 'CREDIT'
    DEBIT = 'DEBIT'
    REVERSAL = 'REVERSAL'
    TYPES = (
        (CREDIT, CREDIT),
        (REVERSAL, REVERSAL),
        (DEBIT, DEBIT)
    )

    public_id = models.CharField(max_length=200,unique=True,null=True)
    trans_id = models.UUIDField(default=uuid.uuid4, editable=False,unique=True, null=True)
    status = models.BooleanField(default=False)
    amount = models.PositiveIntegerField(null=True)
    currency = models.CharField(max_length=200,null=True)
    type = models.CharField(max_length=10, choices=TYPES)
    ref = models.CharField(max_length=200,unique=True,null=True)
    reversalref = models.CharField(max_length=200,unique=True,null=True)
    virtual_account = models.ForeignKey(Virtual_account,on_delete=models.CASCADE,null=True)
    webhook = models.JSONField(null = True, blank = True)
    date_created =models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self) -> str:
        return f'{self.type} : {self.amount}'

    def save(self,*args,**kwargs) -> None:
        while not self.public_id:
            s=secrets.SystemRandom()
            public_id = s.randint(10000000, 99999999)
            public_id = str(public_id)
            object_with_similar_public_id = Transaction.objects.filter(public_id=public_id)
            if not object_with_similar_public_id:
                self.public_id = "RTT"+ public_id
        super().save(*args,**kwargs)


class Refund(models.Model):
    # user = models.ForeignKey(Account, on_delete=models.CASCADE)
    # ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    reason = models.TextField()
    status = models.CharField(
        max_length=10, choices=[("pending", "Pending"), ("approved", "Approved"), ("denied", "Denied")], default="pending"
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)

    def approve_refund(self):
        """Mark refund as approved and process refund"""
        self.status = "approved"
        self.processed_at = now()
        self.ticket.status = "available"  # Release the ticket
        self.ticket.save()
        self.save()

    def deny_refund(self):
        """Deny the refund request"""
        self.status = "denied"
        self.processed_at = now()
        self.save()

        # Send email to user
        subject = "Refund Denied ❌"
        message = f"Hello {self.user.username}, your refund request for ticket {self.ticket.ticket_code} has been denied."
        send_refund_email(self.user.email, subject, message)

    def process_paystack_refund(self):
        """Trigger a refund request to Paystack"""
        transaction = Transaction.list(reference=self.ticket.ticket_code)
        if transaction.get("status") and transaction["data"]:
            trans_id = transaction["data"][0]["id"]
            response = Transaction.refund(trans_id, settings.PAYSTACK_SECRET_KEY)

            if response["status"]:
                self.status = "approved"
                self.processed_at = now()
                self.ticket.status = "available"  # Reset the ticket for resale
                self.ticket.save()
                self.save()
                return True
        return False
