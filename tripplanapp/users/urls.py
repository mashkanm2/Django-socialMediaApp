from django.urls import path,include
from .apis import UserRegisterVerifyOtpCodeView, RegisterApi,ProfileUpdateView,UserAuthentication
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

app_name='users'

urlpatterns = [
    path('register/', RegisterApi.as_view(),name="register"),
    path('verifyCode/', UserRegisterVerifyOtpCodeView.as_view(),name="vrifycode"),
    path('profile/', ProfileUpdateView.as_view(), name='profile-update'),
]+[path("jwt",include(([
        path('login/', UserAuthentication.as_view(),name="login"),
        path('refresh/', TokenRefreshView.as_view(),name="refresh"),
        path('verify/', TokenVerifyView.as_view(),name="verify"),
    ],'jwt'),namespace="jwt"))
]
