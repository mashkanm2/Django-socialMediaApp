from django.urls import path
from .apis import UserRegisterVerifyOtpCodeView, RegisterApi


urlpatterns = [
    path('register/', RegisterApi.as_view(),name="register"),
    path('verifyCode/', UserRegisterVerifyOtpCodeView.as_view(),name="vrifycode"),
]
