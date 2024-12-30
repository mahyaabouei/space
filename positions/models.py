from django.db import models
from companies.models import Company
from user.models import User
from django.utils import timezone



class Position(models.Model):
    EMPLOYMENT_TYPES = [
        ('full_time', 'تمام وقت'),
        ('part_time', 'پاره وقت'),
        ('contract', 'قراردادی'),
        ('freelance', 'فریلنسر'),
        ('internship', 'استخدام آزمایشی'),]

    name = models.CharField(
        max_length=200,
        verbose_name="عنوان شغلی")
    
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name="شرح شغل")
    
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='شرکت')
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name='کاربر')
    
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_positions',
        verbose_name='موقعیت شغلی بالادست')
    
    type_of_employment = models.CharField(
        max_length=20,
        choices=EMPLOYMENT_TYPES,
        null=True,
        blank=True,
        verbose_name='نوع استخدام'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='تاریخ ایجاد')
    
    start_date = models.DateTimeField(
        auto_now_add=False,
        verbose_name='تاریخ شروع')
    
    end_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='تاریخ پایان')

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'موقعیت شغلی'
        verbose_name_plural = 'موقعیت‌های شغلی'

    def __str__(self):
        return f"{self.name} - {self.user}"

    def is_active(self):
        """بررسی فعال بودن موقعیت شغلی"""
        return self.end_date is None