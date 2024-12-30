# استفاده از ایمیج پایه پایتون
FROM python:3.11-slim

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ایجاد و تنظیم دایرکتوری کاری
WORKDIR /app

# کپی فایل‌های requirements
COPY requirements.txt .

# نصب پکیج‌های مورد نیاز
RUN pip install --no-cache-dir -r requirements.txt

# کپی کل پروژه
COPY . .

# اکسپوز کردن پورت ۸۰۰۰
EXPOSE 8000

# دستور اجرای پروژه
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"] 