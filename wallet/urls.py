from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"wallet_info", WalletInfoViewSet, basename="wallet_info")
router.register(r"refunds", RefundViewSet, basename="refunds")

urlpatterns = [
    path('', include(router.urls)),
    path('deposit/', DepositFunds.as_view()),
    path("paystack-webhook/", paystack_webhook, name="paystack-webhook"),
    path('deposit/verify/<str:reference>/', VerifyDeposit.as_view()),
]
