from django.db import models
from accounts.models import Account, Merchant
import secrets
import uuid

# Create your models here.

class Virtual_accounts(models.Model):
    account_name =  models.CharField(max_length=200,null=True)
    account_number =  models.CharField(max_length=200,null=True,unique=True)
    bank_name =  models.CharField(max_length=200,null=True)
    bank_slug =  models.CharField(max_length=200,null=True)
    status =  models.BooleanField(default=False)
    enabled =  models.BooleanField(default=False)
    currency = models.CharField(max_length=200,default="NGN")
    total = models.PositiveIntegerField(default=0,null=True)
    amount_owed = models.PositiveIntegerField(default=0,null=True)
    withdrawable_balance = models.PositiveIntegerField(null=True)
    ledger_balance = models.PositiveIntegerField(null=True)
    merchant = models.ForeignKey(Merchant,on_delete=models.CASCADE, null=True)
    deleted = models.BooleanField(default=False)
    date_created =models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('transfer', 'Transfer'),
    )

    CREDIT = 'CREDIT'
    DEBIT = 'DEBIT'
    REVERSAL = 'REVERSAL'
    TYPES = (
        (CREDIT, CREDIT),
        (REVERSAL, REVERSAL),
        (DEBIT, DEBIT)
    )

    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    recipient = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='received_transactions')
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    public_id = models.CharField(max_length=200,unique=True,null=True)
    trans_id = models.UUIDField(default=uuid.uuid4, editable=False,unique=True, null=True)
    status = models.BooleanField(default=False)
    currency = models.CharField(max_length=200,null=True)
    type = models.CharField(max_length=10, choices=TYPES)
    ref = models.CharField(max_length=200,unique=True,null=True)
    reversalref = models.CharField(max_length=200,unique=True,null=True)
    virtual_account = models.ForeignKey(Virtual_accounts,on_delete=models.CASCADE,null=True)
    merchant = models.ForeignKey(Merchant,on_delete=models.CASCADE,null=True)
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
