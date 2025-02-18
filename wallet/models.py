from django.db import models
<<<<<<< HEAD
from accounts.models import Account, Merchant
=======
# from accounts.models import Account, Merchant
from django.utils import timezone
>>>>>>> 5e1d59cefb2a91bc494d515cc2450e8a9b51980b
import secrets
import uuid

# Create your models here.

<<<<<<< HEAD
=======
class Wallet(models.Model):
    # user = models.OneToOneField(Account, null=True, on_delete=models.CASCADE)
    balance = models.PositiveBigIntegerField(null=True)
    currency = models.CharField(max_length=50, default='NGN')
    created_at = models.DateTimeField(default=timezone.now, null=True)

    def ___str__(self):
        return self.user.__str__()
    

class WalletTransaction(models.Model):

    TRANSACTION_TYPES  = (
        ('deposit', 'deposit'),
        ('transfer','transfer'),
        ('withdraw','withdraw'),
    )
    wallet =  models.ForeignKey(Wallet, null=True, on_delete=models.CASCADE)
    transaction_type =  models.CharField(max_length=200, null=True, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=100, null=True, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now,null=True)
    status = models.CharField(max_length=100, default="pending")
    paystack_payment_reference = models.CharField(max_length=100, default='', blank=True)

    def __str__(self):
        return self.wallet.user.__str__()


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

    # merchant = models.ForeignKey(Merchant,on_delete=models.CASCADE, null=True)
    deleted = models.BooleanField(default=False)
    date_created =models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self) -> str:
        return f'{self.account_name} : {self.account_number}'
    
    # def get_virtual_account(self):
    #     kuda = Kuda()
    #     status,data = kuda.get_virtual_account(self.ref)
    #     if status == True:
    #         info = data['Data']['Account']
    #         self.account_number = info['AccountNumber']
    #         self.account_name = info['AccountName']
    #         self.ref = info['TrackingReference']
    #     self.save()
    #     return status

    # def disable_virtual_account(self):
    #     kuda = Kuda()
    #     status,data = kuda.disable_virtual_account(self.ref)
    #     if status == True:
    #         self.enabled = False
    #         self.save()
    #     return status

    # def enable_virtual_account(self):
    #     kuda = Kuda()
    #     status,data = kuda.enable_virtual_account(self.ref)
    #     if status == True:
    #         self.enabled = True
    #         self.save()
    #     return status

    # def get_virtual_account_balance(self):
    #     kuda = Kuda()
    #     status,data = kuda.get_virtual_account_balance(self.ref)
    #     self.status = status
    #     print(data)
    #     if status == True:
    #         info = data['Data']
    #         self.total = info['AvailableBalance']
    #         self.withdrawable_balance = info['WithdrawableBalance']
    #         self.ledger_balance = info['LedgerBalance']
    #     self.save()
    #     return status,self.total

class Transactions(models.Model):
>>>>>>> 5e1d59cefb2a91bc494d515cc2450e8a9b51980b

    CREDIT = 'CREDIT'
    DEBIT = 'DEBIT'
    REVERSAL = 'REVERSAL'
    TYPES = (
        (CREDIT, CREDIT),
        (REVERSAL, REVERSAL),
        (DEBIT, DEBIT)
    )

<<<<<<< HEAD
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    recipient = models.ForeignKey(Account, null=True, blank=True, on_delete=models.SET_NULL, related_name='received_transactions')
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    public_id = models.CharField(max_length=200,unique=True,null=True)
    trans_id = models.UUIDField(default=uuid.uuid4, editable=False,unique=True, null=True)
    status = models.BooleanField(default=False)
=======
    public_id = models.CharField(max_length=200,unique=True,null=True)
    trans_id = models.UUIDField(default=uuid.uuid4, editable=False,unique=True, null=True)
    status = models.BooleanField(default=False)
    amount = models.PositiveIntegerField(null=True)
>>>>>>> 5e1d59cefb2a91bc494d515cc2450e8a9b51980b
    currency = models.CharField(max_length=200,null=True)
    type = models.CharField(max_length=10, choices=TYPES)
    ref = models.CharField(max_length=200,unique=True,null=True)
    reversalref = models.CharField(max_length=200,unique=True,null=True)
    virtual_account = models.ForeignKey(Virtual_accounts,on_delete=models.CASCADE,null=True)
<<<<<<< HEAD
    merchant = models.ForeignKey(Merchant,on_delete=models.CASCADE,null=True)
=======
    # merchant = models.ForeignKey(Merchant,on_delete=models.CASCADE,null=True)
>>>>>>> 5e1d59cefb2a91bc494d515cc2450e8a9b51980b
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
<<<<<<< HEAD
            object_with_similar_public_id = Transaction.objects.filter(public_id=public_id)
            if not object_with_similar_public_id:
                self.public_id = "RTT"+ public_id
        super().save(*args,**kwargs)
=======
            object_with_similar_public_id = Transactions.objects.filter(public_id=public_id)
            if not object_with_similar_public_id:
                self.public_id = "RTT"+ public_id
        super().save(*args,**kwargs)


>>>>>>> 5e1d59cefb2a91bc494d515cc2450e8a9b51980b
