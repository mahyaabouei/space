from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import  CorrespondencerViewset 

router = DefaultRouter()
router.register(r'', CorrespondencerViewset, basename='sender-correspondence')

urlpatterns = [
    path('', include(router.urls)),
]