from django.db import models

class Announcement (models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="عنوان"
    )
    description = models.TextField(
        verbose_name="توضیحات"
    )
    picture = models.FileField(
        upload_to='media/announcements/' , 
        null=True , 
        blank=True,
        verbose_name="تصویر"
    )
    link = models.CharField(
        max_length=500 , 
        null=True , 
        blank=True,
        verbose_name="لینک"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ به‌روزرسانی"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )
    class Meta:
        verbose_name = "اعلان"
        verbose_name_plural = "اعلان‌ها"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]
    def __str__(self):
        return self.title


class ShortCut (models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name="عنوان"
    )
    picture = models.FileField(
        upload_to='media/shortcuts/' , 
        null=True , 
        blank=True,
        verbose_name="تصویر"
    )
    link = models.CharField(
        max_length=500 , 
        null=True , 
        blank=True,
        verbose_name="لینک"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ به‌روزرسانی"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )
    class Meta:
        verbose_name = "گزینه سریع"
        verbose_name_plural = "گزینه سریع‌ها"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]
    def __str__(self):
        return self.title
