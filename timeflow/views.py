from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models.functions import TruncDate
from .models import UserLoginLog
from rest_framework.permissions import IsAuthenticated

class UserLoginLogAPIView(APIView):
    """
    این API گزارش ورود و خروج کاربران را نمایش می‌دهد.
    برای هر روز:
    - ثبت نام
    - اولین ورود
    - آخرین خروج
    - و جفت‌های ورود-خروج میانی را برمی‌گرداند
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            logs = UserLoginLog.objects.filter(
                user=request.user,
                type__in=['login', 'logout'] 
            ).annotate(
                date=TruncDate('time')
            ).order_by('date', 'time')

            result = {}
            
            for log in logs:
                date_str = log.date.strftime('%Y-%m-%d')
                
                if date_str not in result:
                    result[date_str] = {
                        'first_login': None,
                        'last_logout': None,
                        'intermediate_logs': []
                    }

                if log.type == 'register':
                    result[date_str]['register'] = {
                        'time': log.time.strftime('%H:%M:%S'),
                        'id': log.id,
                        'ip': log.ip_address,
                        'device': log.device_type,
                        'browser': log.browser,
                        'os': log.os_type
                    }

                if log.type == 'login' and result[date_str]['first_login'] is None:
                    result[date_str]['first_login'] = {
                        'time': log.time.strftime('%H:%M:%S'),
                        'id': log.id,
                        'ip': log.ip_address,
                        'device': log.device_type,
                        'browser': log.browser,
                        'os': log.os_type
                    }

                if log.type == 'logout':
                    previous_logout = UserLoginLog.objects.filter(
                        time__lt=log.time,
                        time__gte=log.date,
                        type='logout',
                        user=request.user
                    ).last()

                    if previous_logout:
                        related_login = UserLoginLog.objects.filter(
                            time__gt=previous_logout.time,
                            time__lt=log.time,
                            type='login',
                            user=request.user
                        ).first()
                    else:
                        related_login = UserLoginLog.objects.filter(
                            time__lt=log.time,
                            time__gte=log.date,
                            type='login',
                            user=request.user
                        ).first()

                    if related_login:
                        result[date_str]['intermediate_logs'].append({
                            'login': {
                                'time': related_login.time.strftime('%H:%M:%S'),
                                'id': related_login.id,
                                'ip': related_login.ip_address,
                                'device': related_login.device_type,
                                'browser': related_login.browser,
                                'os': related_login.os_type
                            },
                            'logout': {
                                'time': log.time.strftime('%H:%M:%S'),
                                'id': log.id,
                                'ip': log.ip_address,
                                'device': log.device_type,
                                'browser': log.browser,
                                'os': log.os_type
                            }
                        })

                    result[date_str]['last_logout'] = {
                        'time': log.time.strftime('%H:%M:%S'),
                        'id': log.id,
                        'ip': log.ip_address,
                        'device': log.device_type,
                        'browser': log.browser,
                        'os': log.os_type
                    }

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
