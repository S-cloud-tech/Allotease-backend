from django.urls import path
from .views import WalletInfo, DepositFunds, VerifyDeposit

urlpatterns = [
    path('wallet_info/', WalletInfo.as_view()),
    path('deposit/', DepositFunds.as_view()),
    path('deposit/verify/<str:reference>/', VerifyDeposit.as_view()),
]
