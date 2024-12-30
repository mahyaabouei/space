from django.db import models
from user.models import User
from positions.models import Position
from companies.models import Company
import uuid
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.utils import timezone

class Attache(models.Model):
    name = models.CharField(max_length=255, verbose_name="نام فایل")
    file = models.FileField(
        upload_to="attachments/%Y/%m/",  
        verbose_name="فایل",
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'xlsx', 'xls'])])
    size = models.PositiveIntegerField(verbose_name="حجم فایل (بایت)", editable=False)
    created_at = models.DateTimeField(default=timezone.now,verbose_name="تاریخ ایجاد")

    def save(self, *args, **kwargs):
        if self.file:
            self.size = self.file.size
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = "پیوست"
        verbose_name_plural = "پیوست‌ها"
        indexes = [
            models.Index(fields=['created_at']),
        ]
        
    def __str__(self):
        return f"{self.name} ({self.created_at:%Y-%m-%d})"

class Number(models.Model):
    number = models.IntegerField( verbose_name="شماره")
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="تاریخ ایجاد"
    )
    jalali_year = models.IntegerField(
        verbose_name="سال شمسی",
        null=True,
        blank=True
    )
    company_registration = models.CharField(max_length=20, verbose_name="شماره ثبت", editable=False)
    internal_correspondence = models.BooleanField(default=False, verbose_name="مکاتبه داخلی", editable=False)

    class Meta:
        verbose_name = "شماره مکاتبه"
        verbose_name_plural = "شماره‌های مکاتبات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['number']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return str(self.number)

class Reference(models.Model):
    reference = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        related_name='reference_positions',
        verbose_name="مرجع",)
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="تاریخ خوانده شدن",)
    send_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="تاریخ ارسال",)
    correspondence = models.ForeignKey(
        'Correspondence',
        on_delete=models.PROTECT,
        related_name='reference_correspondences',
        verbose_name="مکاتبه",)
    instruction_text = models.TextField(
        blank=True,
        null=True,
        verbose_name="متن دستور",)
    
    class Meta:
        verbose_name = "مرجع"
        verbose_name_plural = "مراجع"

class Correspondence (models.Model):

    subject = models.CharField(  
        max_length=255,
        blank = True,
        null= True,
        db_index=True,
        verbose_name="موضوع",)
    
    text = models.TextField(
        blank = True,
        null = True,
        verbose_name="متن",)
    
    description = models.TextField(
        blank = True,
        null = True,
        verbose_name="توضیحات",)

    number = models.ForeignKey(
        Number,
        null=True,
        blank= True,
        on_delete=models.PROTECT,
        db_index=True,
        verbose_name="شماره مکاتبه",)
    
    attachments = models.ManyToManyField(
        Attache,
        blank=True,
        verbose_name="پیوست‌ها",
        related_name='correspondences_attachments')
    
    sender = models.ForeignKey(
        Position,
        on_delete=models.PROTECT, 
        related_name='sent_correspondence',
        verbose_name="فرستنده",)
    

    receiver_internal = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='receiver_internal',
        verbose_name="دریافت کننده داخلی",
    )

    receiver_external = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="دریافت کننده خارجی",
    )

    is_internal = models.BooleanField(
        default=True,
        verbose_name="خارجی یا داخلی",)
    
    postcript = models.TextField(
        blank = True,
        null = True,
        verbose_name="پی نوشت",)
    
    seal = models.ForeignKey(
        Company,
        null=True,
        blank=True, 
        to_field='seal',
        on_delete=models.PROTECT,
        related_name='correspondence_seals',
        verbose_name="مهر تجاری",)
    
    signature = models.ForeignKey(
        Company,
        null=True,
        blank=True, 
        to_field='signature',
        on_delete=models.PROTECT,
        related_name='correspondence_signatures',
        verbose_name="امضا",)
    
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name="شناسه یکتا",) 
    
    binding = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="تعهد آور",)
    
    letterhead = models.ForeignKey(
        Company,
        null=True,
        blank=True, 
        to_field='letterhead',
        on_delete=models.PROTECT,
        related_name='correspondence_letterheads',
        verbose_name="سر برگ",)
    
    confidentiality_level = models.CharField(
        max_length=20,
        choices=[
            ('normal', 'عادی'),
            ('confidential', 'محرمانه'),
            ('secret', 'سری'),
            ('top_secret', 'به کلی سری'),],
        default='normal',
        verbose_name="سطح محرمانگی",)
    
    priority = models.CharField(
        max_length=20,
        choices=[
            ('normal', 'عادی'),
            ('immediate', 'فوری'),
            ('very_immediate', 'خیلی فوری'),],
        default='normal',
        verbose_name="اولویت",)

    kind_of_correspondence = models.CharField(
        max_length=20,
        choices=[
            ('announcement', 'اعلامیه'),
            ('request', 'درخواست'),],
        default='request',
        verbose_name="نوع مکاتبه",)
    
    Authority_TYPES = [
        ('new', 'جدید'),
        ('referring_to', 'عطف به'),
        ('following', 'پیرو'),
        ('return_to', 'بازگشت به'),
        ('in_response_to', 'در پاسخ به'),
        ('attached_to', 'به پیوست'),
        ('amendment', 'اصلاحیه'),
    ]

    authority_type = models.CharField(
        max_length=20,
        choices=Authority_TYPES, 
        default='new',
        verbose_name="نوع ارجاع",
    )

    authority_correspondence = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='referencing_correspondences',
        verbose_name="نامه مرجع",
    )

    reference = models.ManyToManyField(
        Reference , 
        blank=True,
        verbose_name="ارجاعات",
        related_name='correspondences_references')
    
    signature_placement = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="امضا",)
    
    seal_placement = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="مهر تجاری",)
    
    draft = models.BooleanField(
        default=True,
        db_index=True,
        verbose_name="پیش‌نویس",)
    
    published = models.BooleanField(
        default=False,
        db_index=True,
        verbose_name="انتشار",)
    
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="تاریخ ایجاد",)
    
    updated_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name="تاریخ به‌روزرسانی",)
    
    received_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="تاریخ دریافت",)
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        verbose_name="تاریخ خوانده شدن",)
    
    class Meta:
        verbose_name = "مکاتبه"
        verbose_name_plural = "مکاتبات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['uuid']),
        ]
    def __str__(self):
        return f"{self.number} - {self.subject} ({self.created_at:%Y-%m-%d})"
    


    


    