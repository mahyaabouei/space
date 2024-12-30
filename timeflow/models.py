from django.conf import settings
from django.db import models
from django.utils import timezone

class UserLoginLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    # زمان و تاریخ
    time = models.DateTimeField(default=timezone.now)
    type = models.CharField(max_length=10 , choices=[('login' , 'ورود') , ('logout' , 'خروج')  , ('register' , 'ثبت نام') , ('refresh' , 'تازه سازی')])
    # اطلاعات سیستم
    ip_address = models.GenericIPAddressField()
    device_type = models.CharField(max_length=200 , null=True , blank=True)  # موبایل/دسکتاپ
    os_type = models.CharField(max_length=200 , null=True , blank=True)      # سیستم عامل
    browser = models.CharField(max_length=500 , null=True , blank=True)     # مرورگر
    # اطلاعات اضافی
    user_agent = models.TextField()       # User-Agent کامل
    class Meta:
        ordering = ['-time']
        verbose_name = 'لاگ ورود و خروج کاربر'
        verbose_name_plural = 'لاگ ورود و خروج کاربر'
    def __str__(self):
        return f"{self.user.username} - {self.time}"
    def duration(self):
        """محاسبه مدت زمان session"""
        if self.type == 'logout':
            return self.time - self.time
        return None


