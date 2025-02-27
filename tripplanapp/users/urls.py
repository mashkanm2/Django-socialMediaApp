from django.urls import path
from .apis import UserRegisterVerifyOtpCodeView, RegisterApi,ProfileUpdateView

app_name='users'

urlpatterns = [
    path('register/', RegisterApi.as_view(),name="register"),
    path('verifyCode/', UserRegisterVerifyOtpCodeView.as_view(),name="vrifycode"),
    path('profile/', ProfileUpdateView.as_view(), name='profile-update'),
]
