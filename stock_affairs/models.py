from django.db import models
from companies.models import Company
from django.utils import timezone
from user.models import User
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError
from transactions.models import PaymentGateway , Payment

class Shareholders(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="نام سهامدار"
    )
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        verbose_name="شرکت"
    )
    number_of_shares = models.PositiveBigIntegerField(verbose_name="تعداد سهام")
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ به‌روزرسانی",
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = "سهامدار"
        verbose_name_plural = "سهامداران"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.company}"
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if Shareholders.objects.filter(user=self.user, company=self.company).exists():
            raise ValidationError({
                "error": "این کاربر قبلاً در این شرکت به عنوان سهامدار ثبت شده است"
            })


class StockTransfer(models.Model):
    seller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='stock_sales',
        verbose_name="فروشنده"
    )
    buyer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='stock_purchases',
        verbose_name="خریدار"
    )
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        verbose_name="شرکت"
    )
    number_of_shares = models.BigIntegerField(verbose_name="تعداد سهام")
    document = models.FileField(
        upload_to='stock_affairs/documents/',
        null=True, 
        blank=True,
        verbose_name="سند"
    )
    price = models.BigIntegerField(verbose_name="قیمت")
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ به‌روزرسانی"
    )

    class Meta:
        verbose_name = "انتقال سهام"
        verbose_name_plural = "انتقال‌های سهام"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]
    def __str__(self):
        return f"{self.seller} - {self.buyer} - {self.company}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.seller == self.buyer:
            raise ValidationError({
                "error": "فروشنده و خریدار نمی‌توانند یک شخص باشند"
            })


class Precedence(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="کاربر"
    )
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        verbose_name="شرکت"
    )
    precedence = models.BigIntegerField(verbose_name="حق تقدم")
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ به‌روزرسانی"
    )

    class Meta:
        verbose_name = "حق تقدم"
        verbose_name_plural = "حق تقدم‌ها"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.company}"
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if Precedence.objects.filter(user=self.user, company=self.company).exists():
            raise ValidationError({
                "error": "شما قبلا حق تقدم در این شرکت ثبت کرده اید"
            })
    


class CapitalIncreasePayment(models.Model):
    document = models.FileField(
        upload_to='stock_affairs/documents/',
        verbose_name="سند"
    )
    precedence = models.ForeignKey(
        Precedence, 
        on_delete=models.CASCADE,
        verbose_name="حق تقدم"
    )
    amount = models.BigIntegerField(verbose_name="مقدار")
    value = models.BigIntegerField(verbose_name="قیمت")
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ به‌روزرسانی"
    )
    class Meta:
        verbose_name = "پرداخت حق تقدم"
        verbose_name_plural = "پرداخت‌های حق تقدم"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.precedence}"


class DisplacementPrecedence(models.Model):
    seller = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='precedence_sales',
        verbose_name="فروشنده"
    )
    buyer = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='precedence_purchases',
        verbose_name="خریدار"
    )
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        verbose_name="شرکت"
    )
    number_of_shares = models.BigIntegerField(verbose_name="تعداد سهام")
    price = models.BigIntegerField(verbose_name="قیمت")
    document = models.FileField(
        upload_to='stock_affairs/documents/',
        null=True, 
        blank=True,
        verbose_name="سند"
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
        verbose_name = "انتقال حق تقدم"
        verbose_name_plural = "انتقال‌های حق تقدم"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.seller} - {self.buyer} - {self.company}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        if self.seller == self.buyer:
            raise ValidationError({
                "error": "فروشنده و خریدار نمی‌توانند یک شخص باشند"
            })



class ProcessDescription(models.Model):
    description = models.TextField(
        null=True , 
        blank=True , 
        verbose_name="توضیحات"
    )
    picture = models.ImageField(
        upload_to='stock_affairs/process_description/',
        null=True , 
        blank=True , 
        verbose_name="تصویر"
    )
    title = models.CharField(
        max_length=255,
        null=True , 
        blank=True , 
        verbose_name="عنوان"
    )
    location = models.CharField(
        max_length=255,
        null=True , 
        blank=True , 
        verbose_name="مکان"
    )
    contact_number = models.CharField(
        max_length=255,
        null=True , 
        blank=True , 
        verbose_name="شماره تماس"
    )
    instagram_link = models.URLField(
        null=True , 
        blank=True , 
        verbose_name="لینک آی‌دی اینستاگرام"
    )
    telegram_link = models.URLField(
        null=True , 
        blank=True , 
        verbose_name="لینک تلگرام"
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
        verbose_name = "توضیحات فرایند"
        verbose_name_plural = "توضیحات فرایند"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title}"


class UnusedPrecedenceProcess(models.Model):
    company = models.ForeignKey(
        Company, 
        on_delete=models.CASCADE,
        verbose_name="شرکت"
    )
    total_amount = models.BigIntegerField(
        verbose_name=" مقدار کل"
    )
    used_amount = models.BigIntegerField(
        verbose_name=" مقدار موجود"
    )
    price = models.BigIntegerField(
        verbose_name="قیمت"
    )
    process_description = models.ForeignKey(
        ProcessDescription,
        on_delete=models.CASCADE,
        null=True , 
        blank=True , 
        verbose_name="توضیحات فرایند"
    )
    agreement = models.BooleanField(
        default=True , 
        verbose_name="موافقت نامه"
    )
    payment_gateway = models.ForeignKey(
        PaymentGateway , 
        on_delete=models.CASCADE , 
        null=True , 
        blank=True , 
        verbose_name="درگاه پرداخت"
    )
    business_plan = models.FileField(
        upload_to='stock_affairs/business_plans/',
        null=True , 
        blank=True , 
        verbose_name="فایل طرح کسب و کار" 
    )
    business_plan_description = models.TextField(
        null=True , 
        blank=True , 
        verbose_name="توضیحات طرح کسب و کار"
    )
    business_plan_regulator = models.CharField(
        max_length=255,
        null=True , 
        blank=True , 
        verbose_name="نام تنظیم کننده طرح کسب و کار"
    )
    business_plan_regulator_logo = models.FileField(
        upload_to='stock_affairs/business_plan_regulator_logos/',
        null=True , 
        blank=True , 
        verbose_name="لوگو تنظیم کننده طرح کسب و کار"
    )
    progress_plan = models.FileField(
        upload_to='stock_affairs/progress_plan/',
        null=True , 
        blank=True , 
        verbose_name="فایل پیشرفت طرح کسب و کار"
    )
    progress_plan_description = models.TextField(
        null=True , 
        blank=True , 
        verbose_name="توضیحات پیشرفت طرح کسب و کار"
    )
    progress_plan_regulator = models.CharField(
        max_length=255,
        null=True , 
        blank=True , 
        verbose_name="نام تنظیم کننده پیشرفت طرح کسب و کار"
    )
    progress_plan_regulator_logo = models.FileField(
        upload_to='stock_affairs/progress_plan_regulator_logos/',
        null=True , 
        blank=True , 
        verbose_name="لوگو تنظیم کننده پیشرفت طرح کسب و کار"
    )
    validation = models.FileField(
        upload_to='stock_affairs/validation/',
        null=True , 
        blank=True , 
        verbose_name="فایل اعتبار سنجی طرح کسب و کار"
    )
    validation_description = models.TextField(
        null=True , 
        blank=True , 
        verbose_name="توضیحات اعتبار سنجی طرح کسب و کار"
    )
    validation_regulator = models.CharField(
        max_length=255,
        null=True , 
        blank=True , 
        verbose_name="نام تنظیم کننده اعتبار سنجی طرح کسب و کار"
    )
    validation_regulator_logo = models.FileField(
        upload_to='stock_affairs/validation_regulator_logos/',
        null=True , 
        blank=True , 
        verbose_name="لوگو تنظیم کننده اعتبار سنجی طرح کسب و کار"
    )
    share_expert = models.FileField(
        upload_to='stock_affairs/share_expert/',
        null=True , 
        blank=True , 
        verbose_name="فایل کارشناس سهام"
    )
    share_expert_description = models.TextField(
        null=True , 
        blank=True , 
        verbose_name="توضیحات کارشناس سهام"
    )
    share_expert_regulator = models.CharField(
        max_length=255,
        null=True , 
        blank=True , 
        verbose_name="نام تنظیم کننده کارشناس سهام"
    )
    share_expert_regulator_logo = models.FileField(
        upload_to='stock_affairs/share_expert_regulator_logos/',
        null=True , 
        blank=True , 
        verbose_name="لوگو تنظیم کننده کارشناس سهام"
    )
    gallery = models.URLField(
        max_length=1000,
        null=True,
        blank=True,
        verbose_name="گالری"
    )
    is_active = models.BooleanField(
        default=True , 
        verbose_name="فعال"
    )
    sheba_number = models.CharField(
        max_length=255,
        null=True , 
        blank=True , 
        verbose_name="شماره شبا"
    )
    end_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="تاریخ اتمام "
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
        verbose_name = "ایجاد فرایند پذیره نویسی"
        verbose_name_plural = "فرایند پذیره نویسی"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.company}"

class FinancialStatementUnusedPrecedenceProcess(models.Model):
    unused_precedence_process = models.OneToOneField(
        UnusedPrecedenceProcess,
        on_delete=models.CASCADE,
        related_name='financial_statement',
        null=True,
        blank=True,
        verbose_name="فرایند پذیره نویسی"
    )
    title = models.CharField(
        max_length=255,
        verbose_name="عنوان"
    )
    file = models.FileField(
        null=True , 
        blank=True , 
        upload_to='stock_affairs/financial_statements/',
        verbose_name="فایل"
    )
    link = models.URLField(
        null=True , 
        blank=True , 
        verbose_name="لینک"
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
        verbose_name = "صورت های مالی"
        verbose_name_plural = "صورت های مالی"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.title}"


class Appendices(models.Model):
    file = models.FileField(
        upload_to='stock_affairs/appendices/',
        verbose_name="فایل"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="نام"
    )
    unused_precedence_process = models.OneToOneField(
        UnusedPrecedenceProcess,
        on_delete=models.CASCADE,
        related_name='appendices',
        null=True,
        blank=True,
        verbose_name=" فرایند پذیره نویسی"
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
        verbose_name = "ضمیمه"
        verbose_name_plural = "ضمیمه‌ها"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.name}"


class Underwriting(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="کاربر"
    )
    requested_amount = models.BigIntegerField(
        null=True ,
        blank=True,
        verbose_name="مقدار درخواست شده"
    )
    type = models.CharField(
        max_length=255 , 
        null=True , 
        blank=True , 
        choices=[('1' , '1') , ('2' , '2')],
        # 1 : فیش
        # 2 : درگاه پرداخت
        verbose_name="نوع"
    )
    price = models.BigIntegerField(
        null=True , 
        blank=True,
        verbose_name="قیمت"
    )
    process = models.ForeignKey(
        UnusedPrecedenceProcess, 
        on_delete=models.CASCADE, 
        verbose_name="فرایند"
    )
    document = models.FileField(
        upload_to='stock_affairs/documents/' , 
        null=True , 
        blank=True, 
        verbose_name="تصویر فیش"
    )
    payment = models.ForeignKey(
        Payment , 
        on_delete=models.CASCADE , 
        null=True , 
        blank=True , 
        verbose_name="پرداخت"
    )
    description = models.TextField(
        null=True , 
        blank=True , 
        verbose_name="توضیحات"
    )
    status = models.CharField(
        max_length=255 , 
        null=True , 
        blank=True , 
        choices=[('pending' , 'pending') , ('approved' , 'approved') , ('rejected' , 'rejected')],
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
        verbose_name = "پذیره نویسی "
        verbose_name_plural = "پذیره نویسی "
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user}"



