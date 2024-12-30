from django.db import models
from django.utils import timezone
from companies.models import Company

class PaymentGateway(models.Model):
    name = models.CharField(
        max_length=255 , 
        null=True , 
        blank=True ,
        verbose_name="نام درگاه"
    )
    description = models.TextField(
        null=True , 
        blank=True ,
        verbose_name="توضیحات"
    )
    base_url = models.CharField(max_length=500 , null=True , blank=True)
    redirect_url = models.CharField(
        max_length=500 , 
        null=True , 
        blank=True ,
        verbose_name="آدرس هدایت"
    )
    username  = models.CharField(
        max_length=255 , 
        null=True , 
        blank=True ,
        verbose_name="نام کاربری"
    )
    password = models.CharField(
        max_length=255 , 
        null=True , 
        blank=True ,
        verbose_name="رمز عبور"
    )
    terminal_number = models.CharField(
        max_length=255 , 
        null=True , 
        blank=True ,
        verbose_name="شماره ترمینال"
    )
    company = models.ForeignKey(
        Company , 
        on_delete=models.CASCADE , 
        null=True , 
        blank=True ,
        verbose_name="شرکت"
    )
    card_number = models.CharField(
        max_length=255 , 
        null=True , 
        blank=True ,
        verbose_name="شماره کارت"
    )
    is_active = models.BooleanField(
        default=True ,
        verbose_name="وضعیت"
    )
    created_at = models.DateTimeField(
        auto_now_add=True ,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True ,
        verbose_name="تاریخ بروزرسانی"
    )
    
    class Meta:
        verbose_name = "درگاه پرداخت"
        verbose_name_plural = "درگاه پرداخت"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name}"



class Payment(models.Model):
    payment_gateway = models.ForeignKey(
        PaymentGateway , 
        on_delete=models.CASCADE , 
        verbose_name="درگاه پرداخت"
    )

    invoice_unique_id = models.CharField(
        max_length=255 , 
        verbose_name="شناسه فاکتور"
    )
    error_code = models.CharField(
        max_length=255 , 
        verbose_name="کد خطا"
    )
    error = models.CharField(
        max_length=255 , 
        verbose_name="خطا"
    )
    transaction_url = models.CharField(
        max_length=255 , 
        verbose_name="آدرس تراکنش"
    )
    verify_transaction = models.BooleanField(
        default=False , 
        verbose_name="تراکنش بررسی شده"
    )
    code_payment = models.CharField(
        max_length=255 , 
        verbose_name="کد پرداخت"
    )
    refrence_number = models.CharField(
        max_length=255 , 
        verbose_name="شماره پیگیری شاپرک"
    )
    code_state_payment = models.CharField(
        max_length=255 , 
        verbose_name="کد وضعیت پرداخت"
    )
    cart_number = models.CharField(
        max_length=255 , 
        verbose_name="شماره کارت"
    )
    hashed_cart_number = models.CharField(
        max_length=255 , 
        verbose_name="شماره کارت مجموعه شده"
    )
    referal_number = models.CharField(
        max_length=255 , 
        verbose_name="شماره مرجع"
    )
    track_id = models.CharField(
        max_length=255 , 
        verbose_name="شماره پیگیری"
    )
    status = models.CharField(
        max_length=255 , 
        null=True , 
        blank=True , 
        choices=[('pending' , 'درحال بررسی') , ('approved' , 'تایید شده') , ('rejected' , 'رد شده')] , 
        verbose_name="وضعیت"
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ به‌روزرسانی"
    )

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.invoice_unique_id} - {self.payment_gateway.name}"

