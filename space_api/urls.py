from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import routers

router = routers.DefaultRouter()


urlpatterns = [
    path('admin/', admin.site.urls),
    path('' , include('user.urls')),
    path('' , include('authentication.urls')),
    path('companies/' , include('companies.urls')),
    path('positions/' , include('positions.urls')),
    path('correspondence/', include('correspondence.urls')),
    path('stock_affairs/' , include('stock_affairs.urls')),
    path('core/' , include('core.urls')),
    path('timeflow/' , include('timeflow.urls')),
    path('transactions/' , include('transactions.urls')),
]

# سرو فایل‌های استاتیک و مدیا در هر حالت
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)