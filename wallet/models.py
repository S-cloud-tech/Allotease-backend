from django.db import models
from .kuda import Kuda_model
import uuid
import secrets

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
    deleted = models.BooleanField(default=False)
    date_created =models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-date_created',)

    def __str__(self) -> str:
        return f'{self.account_name} : {self.account_number}'
    
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

class Transactions(models.Model):

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
    virtual_account = models.ForeignKey(Virtual_accounts,on_delete=models.CASCADE,null=True)
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
            object_with_similar_public_id = Transactions.objects.filter(public_id=public_id)
            if not object_with_similar_public_id:
                self.public_id = "RTT"+ public_id
        super().save(*args,**kwargs)

