from django.urls import path, include
from .views import *

urlpatterns = [
    path('allauth/', include('allauth.urls')),
    path('register/', RegisterView.as_view(), name="register_user"),
    path('login/', LoginView.as_view(), name='login_user'),
    path('delete/', DeleteUser.as_view(), name='delete_user'),
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('password-reset-request/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/', PasswordResetView.as_view(), name='password_reset'),


    # path('driver/register-form/', views.CreateDriver.as_view(), name ='register_driver_form'),
    # path('driver/register-form/', views.CreateDriver.as_view(), name ='save_driver_form'),
]
