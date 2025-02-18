from django.contrib import admin
<<<<<<< HEAD
from .models import Virtual_accounts


# Register your models here.
admin.site.register(Virtual_accounts)
=======
from .models import Wallet, WalletTransaction


# Register your models here.
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
>>>>>>> 5e1d59cefb2a91bc494d515cc2450e8a9b51980b
