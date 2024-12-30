from django.contrib import admin
from transactions.models import Payment , PaymentGateway
# Register your models here.

admin.site.register(Payment)
admin.site.register (PaymentGateway)
class PaymentGatewayAdmin(admin.ModelAdmin):
    list_display = ['name' , 'is_active' , 'company']
    list_filter = ['is_active' , 'company']
    search_fields = ['name' , 'company__name']
    list_per_page = 100
    ordering =  ['-created_at']
    list_editable = ['is_active']
    list_display_links = ['name']
    list_select_related = ['name']
    fieldsets = [
        ('اطلاعات پرداخت', {
            'fields': ['name', 'description' , 'company']
        }),
        ('تنظیمات', {
            'fields': ['base_url', 'username', 'password', 'terminal_number', 'card_number']
        }),
        ('وضعیت', {
            'fields': ['is_active']
        }),
    ]

