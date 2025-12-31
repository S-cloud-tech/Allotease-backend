from django.urls import path
from .views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('signup/', RegularUserSignupView.as_view(), name='signup-regular'),
    path('register/', RegisterView.as_view(), name="register_user"),
    path('login/', LoginView.as_view(), name='login_user'), # General Login endpoint
    # path('delete/', DeleteUser.as_view(), name='delete_user'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),

    # Merchant Endpoints
    path('signup/', MerchantSignupView.as_view(), name='signup-merchant'),
    path('register/', CreateMerchant.as_view(), name ='register_merchant_form'),
    path('profile/', AccountProfileView.as_view(), name='user_profile'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
