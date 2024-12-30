from django.contrib import admin
from .models import UserLoginLog

@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'time',
        'type',
        'ip_address',
        'device_type',
        'os_type',
        'browser',
        'user_agent'
    )
    
    list_filter = (
        'device_type',
        'os_type',
        'browser',
        'time'
    )
    
    search_fields = (
        'user__username',
        'ip_address',
        'user_agent'
    )
    
    readonly_fields = (
        'time',
        'ip_address',
        'device_type',
        'os_type',
        'browser',
        'user_agent'
    )
    
    fieldsets = (
        ('اطلاعات کاربر', {
            'fields': ('user',)
        }),
        ('زمان‌بندی', {
            'fields': ('time',)
        }),
        ('اطلاعات سیستم', {
            'fields': ('ip_address', 'device_type', 'os_type', 'browser')
        }),
        ('اطلاعات تکمیلی', {    
            'fields': ('user_agent',),
            'classes': ('collapse',)
        })
    )