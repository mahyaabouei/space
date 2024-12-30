from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import UserLoginLog

class CustomJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        # احراز هویت اصلی
        auth_response = super().authenticate(request)
        
        if auth_response is not None:
            user, token = auth_response
            # ثبت لاگ
            UserLoginLog.objects.create(
                user=user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                type='login',
                login_status=True,
                device_type=request.META.get('HTTP_USER_AGENT', ''),
                os_type=request.META.get('HTTP_USER_AGENT', ''),
                browser=request.META.get('HTTP_USER_AGENT', ''),
                
            )
            
        return auth_response
