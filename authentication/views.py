from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.utils.decorators import method_decorator
from django_ratelimit.decorators import ratelimit
from GuardPyCaptcha.Captch import GuardPyCaptcha
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.contrib.auth.models import Group 
from .serializer import GroupSerializer
from django.contrib.auth import get_user_model
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from timeflow.models import UserLoginLog
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.utils import timezone
import user_agents  
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from django.contrib.auth.models import Permission
from .serializer import PermissionSerializer
from user.models import User
from stock_affairs.permission import IsUnusedPrecedenceProcess , IsPrecedence , IsShareholder , IsUnderwriting

class CaptchaViewset(APIView) :
    permission_classes = [AllowAny]
    @method_decorator(ratelimit(key='ip', rate='5/m', method='GET', block=True))
    def get (self,request):
        captcha = GuardPyCaptcha ()
        captcha = captcha.Captcha_generation(num_char=4 , only_num= True)
        return Response ({'captcha' : captcha} , status = status.HTTP_200_OK)

    
class GroupManagementViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        try:
            name = request.data.get('name')
            permissions = request.data.get('permissions', [])

            group = Group.objects.create(name=name)
            
            if permissions:
                group.permissions.set(permissions)
            serializer = self.get_serializer(group)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            name = request.data.get('name')
            permissions = request.data.get('permissions', [])

            if name:
                instance.name = name
            
            if permissions:
                instance.permissions.set(permissions)
            
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        

User = get_user_model()
class UserToGroupViewSet(ModelViewSet):
    permission_classes = [IsAdminUser]
    
    def assign_group(self, request):
        try:
            user_id = request.data.get('user_id')
            group_ids = request.data.get('groups', [])
            
            user = User.objects.get(id=user_id)
            
            user.groups.set(group_ids)
            
            return Response({
                'message': 'کاربر با موفقیت به گروه‌ها اضافه شد',
                'user': user.username,
                'groups': list(user.groups.values_list('name', flat=True))
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response(
                {'error': 'کاربر مورد نظر یافت نشد'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "refresh_token is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            try:
                # تبدیل رشته به شیء RefreshToken
                token = RefreshToken(refresh_token)
                # بلک‌لیست کردن توکن
                token.blacklist()
            except TokenError as e:
                return Response(
                    {"error": f"Invalid token: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            UserLoginLog.objects.create(
                user=request.user,
                type='logout',
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT')
            )
            
            return Response(
                {"detail": "Successfully logged out"}, 
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # پیدا کردن کاربر از طریق نام کاربری ارسال شده
            username = request.data.get('username')
            user = User.objects.get(username=username)
            
            # دریافت اطلاعات درخواست
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
                
            user_agent = request.META.get('HTTP_USER_AGENT', '')
            device_type = 'موبایل' if 'Mobile' in user_agent else 'دسکتاپ'
            
            # ایجاد لاگ ورود با کاربر پیدا شده
            UserLoginLog.objects.create(
                user=user,  # استفاده از کاربر پیدا شده به جای request.user
                type='login',
                ip_address=ip,
                device_type=device_type,
                user_agent=user_agent
            )
            
        return response
    

class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        # ابتدا پاسخ را دریافت می‌کنیم
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            try:
                refresh_token = request.data.get('refresh')
                token = RefreshToken(refresh_token)
                # دریافت کاربر از توکن
                user_id = token.payload.get('user_id')
                user = User.objects.get(id=user_id)

                # دریافت User-Agent
                user_agent_string = request.META.get('HTTP_USER_AGENT', '')
                user_agent = user_agents.parse(user_agent_string)
                
                # ثبت لاگ
                UserLoginLog.objects.create(
                    user=user,  # استفاده از کاربر استخراج شده از توکن
                    time=timezone.now(),
                    type='refresh',
                    ip_address=request.META.get('REMOTE_ADDR'),
                    device_type='Mobile' if user_agent.is_mobile else 'Desktop',
                    os_type=user_agent.os.family,
                    browser=f"{user_agent.browser.family} {user_agent.browser.version_string}",
                    user_agent=user_agent_string
                )
            except Exception as e:
                # در صورت بروز خطا در ثبت لاگ، فقط لاگ را نادیده می‌گیریم
                # و همچنان پاسخ موفق را برمی‌گردانیم
                pass
        
        return response
    


class PermissionListView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        permissions = Permission.objects.all()
        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)
    

class SetUserPermissionView(APIView):
    permission_classes = [IsAdminUser]
    def post(self, request):
        user_id = request.data.get('user_id')
        permissions_list  = request.data.get('permission_id')
        user = User.objects.get(id=user_id)
        user.user_permissions.clear()

        for permission_id in permissions_list:
            permission = Permission.objects.get(id=permission_id)
            user.user_permissions.add(permission)
        user.save()
        return Response({"message": "Permission set successfully"})


class PermissionListForUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if user.is_superuser or user.is_staff:
            permission_names = user.get_all_permissions()
            permissions = Permission.objects.filter(
                codename__in=[perm.split('.')[-1] for perm in permission_names]
            )
        else:
            permissions = user.user_permissions.all()
        unused_precedence_process_perm = IsUnusedPrecedenceProcess()
        precedence_perm = IsPrecedence()
        shareholder_perm = IsShareholder()
        underwriting_perm = IsUnderwriting()
        
        perm_data_unused_precedence_process = unused_precedence_process_perm.get_permission_data(request, self)
        perm_data_precedence = precedence_perm.get_permission_data(request, self)
        perm_data_shareholder = shareholder_perm.get_permission_data(request, self)
        perm_data_underwriting = underwriting_perm.get_permission_data(request, self)
        
        permissions = list(permissions)
        if perm_data_unused_precedence_process:
            permissions.append(perm_data_unused_precedence_process)
        if perm_data_precedence:
            permissions.append(perm_data_precedence)
        if perm_data_shareholder:
            permissions.append(perm_data_shareholder)
        if perm_data_underwriting:
            permissions.append(perm_data_underwriting)
    

        serializer = PermissionSerializer(permissions, many=True)
        return Response(serializer.data)

        


           
            
 