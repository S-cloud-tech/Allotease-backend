from django.urls import path, include
from .views import *
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from accounts import router as users_api_router

api_url_patterns = [
    path(r'', include(users_api_router.router.urls))
]


urlpatterns = [
    path('allauth/', include('allauth.urls')),
    path('signup/regular/', RegularUserSignupView.as_view(), name='signup-regular'),
    path('register/', RegisterView.as_view(), name="register_user"),
    path('login/', LoginView.as_view(), name='login_user'), # General Login endpoint
    # path('delete/', DeleteUser.as_view(), name='delete_user'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),

    # Merchant Endpoints
    path('signup/merchant/', MerchantSignupView.as_view(), name='signup-merchant'),
    path('merchant/register-form/', CreateMerchant.as_view(), name ='register_merchant_form'),
    path('profile/', AccountProfileView.as_view(), name='user_profile'),
    path('', include(api_url_patterns)),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
