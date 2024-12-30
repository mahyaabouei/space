import requests
from typing import Optional
import os


class NotificationService:
    def __init__(self, sms_config: dict = None, email_config: Optional[dict] = None):
        # استفاده از کانفیگ پیش‌فرض
        if sms_config is None:
            # اینجا باید مقدار پیش‌فرض را از تنظیمات جانگو یا محیط بگیرید
            default_config = {
                'from': os.getenv('SMS_FROM'),
                'username': os.getenv('SMS_USERNAME'),
                'password': os.getenv('SMS_PASSWORD'),
                'url': os.getenv('SMS_URL')
            }
            sms_config = default_config

        if isinstance(sms_config, dict):
            self.sms_from = sms_config.get('from')
            self.sms_username = sms_config.get('username')
            self.sms_password = sms_config.get('password')
            self.sms_url = sms_config.get('url')
        else:
            raise ValueError("sms_config باید یک دیکشنری معتبر باشد")

        self.email_config = email_config

    def send_sms(self, to: str, message: str, template: Optional[str] = None) -> dict:
        """
        ارسال پیامک با متن و گیرنده دلخواه
        
        :param to: شماره گیرنده
        :param message: متن پیام
        :param template: قالب پیام (اختیاری)
        :return: پاسخ API
        """
        if template:
            message = self._apply_template(template, message)
            
        params = {
            'from': self.sms_from,
            'to': to,
            'username': self.sms_username,
            'password': self.sms_password,
            'message': message
        }
        
        response = requests.get(url=self.sms_url, params=params)
        return response.json()
    
    def _apply_template(self, template: str, message: str) -> str:
        """
        اعمال قالب روی متن پیام
        """
        templates = {
            'password_reset': f'اتوماسیون اداری ایساتیس پویا\n فراموشی رمز عبور\n کد: {message}',
            'set_password': f'اتوماسیون اداری ایساتیس پویا\nرمز عبور شما :\n{message}',
            'notification': f'اتوماسیون اداری ایساتیس پویا\n {message}',
        }
        return templates.get(template, message)

    def send_email(self, to: str, subject: str, body: str):
        """
        برای پیاده‌سازی در آینده
        """
        pass

