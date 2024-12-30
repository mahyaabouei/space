from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'announcements', views.AnnouncementView, basename='announcement')
router.register(r'shortcuts', views.ShortCutView, basename='shortcut')

urlpatterns = [
    path('', include(router.urls)),
    path('menu/', views.MenuView.as_view(), name='menu'),
]

