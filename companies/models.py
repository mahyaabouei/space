from django.db import models
from django.core.validators import FileExtensionValidator



class Company(models.Model):
    name = models.CharField(max_length=255 , verbose_name="نام شرکت")
    description = models.TextField(verbose_name="توضیحات")
    address = models.TextField(verbose_name="آدرس")

    phone = models.CharField(max_length=20,verbose_name="تلفن")
    email = models.EmailField(verbose_name="ایمیل")
    website = models.URLField(verbose_name="وب سایت")

    postal_code = models.CharField(
        max_length=15,
        null=True,
        blank = True,
        verbose_name="کد پستی")
    
    national_id = models.CharField(
        max_length=20,
        verbose_name="شناسه ملی")
    
    year_of_establishment = models.PositiveSmallIntegerField(verbose_name="سال تاسیس")
    registration_number = models.PositiveIntegerField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="شماره ثبت")
    
    registered_capital = models.BigIntegerField(
            null=True,
            blank=True ,
            verbose_name="سرمایه ثبتی",
            help_text="مقدار به ریال وارد شود")
    
    
    type_of_activity = models.CharField(
        max_length=255,
        verbose_name="نوع فعالیت")
    
    company_type = models.CharField(max_length=100,
        verbose_name="نوع شرکت",
        choices=[
            ('private_joint_stock', 'سهامی خاص'),
            ('public_joint_stock', 'سهامی عام'),
            ('limited_liability', 'مسئولیت محدود'),
            ('general_partnership', 'تضامنی'),
            ('non_stock_mixed', 'مختلط غیر سهامی'),
            ('stock_mixed', 'مختلط سهامی'),
            ('proportional_liability', 'نسبی'),
            ('cooperative', 'تعاونی تولید و مصرف'),
        ])
    
    logo = models.ImageField(
        upload_to='company/logo/',
        null=True, blank=True,
        verbose_name="لوگو",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg'])])
    
    seal = models.ImageField(
        upload_to='company/seal/',
        null=True, blank=True,
        unique=True,
        verbose_name="مهر تجاری",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg'])])
    

    signature = models.ImageField(
        upload_to='company/signature/',
        null=True, blank=True,
        unique=True,
        verbose_name="امضا",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg'])])
    
    letterhead = models.ImageField(
        upload_to='company/letterhead/',
        null=True, blank=True,
        unique=True,
        verbose_name="سر برگ",
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'svg'])])

    class Meta:
        verbose_name = "شرکت"
        verbose_name_plural = "شرکت ها"
        indexes = [
            models.Index(fields=['national_id']),
        ]

    def __str__(self):
        return self.name

