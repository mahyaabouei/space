# مشاهده لاگ‌های زنده
```bash
sudo journalctl -u space-api -f
```

# ری‌استارت سرویس
```bash
sudo systemctl restart space-api
```

# مشاهده لاگ‌های خطا
```bash
tail -f /var/log/gunicorn/error.log
```

# مشاهده لاگ‌های دسترسی
```bash
tail -f /var/log/gunicorn/access.log
```

# فیلتر کردن فرآیندهای گانیکورن
```bash
htop -p $(pgrep -d',' gunicorn)
```

# وضعیت کلی سرویس
```bash
watch -n 1 "systemctl status space-api"
```

# آمار مصرف منابع
```bash
ps aux | grep gunicorn
```


# بررسی اتصالات فعال به پورت 2083
```bash
watch -n 1 "netstat -tulpn | grep 2083"
```