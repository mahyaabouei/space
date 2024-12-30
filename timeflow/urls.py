from django.urls import path
from .views import UserLoginLogAPIView

urlpatterns = [
    path('user-login-logs/', UserLoginLogAPIView.as_view(), name='user-login-logs'),
]
