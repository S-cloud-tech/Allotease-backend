from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (RegisterView, LoginView, SendOTPView, 
                    VerifyOTPView, PasswordResetRequestView, 
                    PasswordResetView, AccountProfileView, 
                    )

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    path('login/', LoginView.as_view(), name='login'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),
    path('profile/', AccountProfileView.as_view(), name='user_profile'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
