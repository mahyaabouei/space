from .views import  CaptchaViewset, GroupManagementViewSet , UserToGroupViewSet, PermissionListView , SetUserPermissionView , PermissionListForUserView , LogoutView, CustomTokenObtainPairView, CustomTokenRefreshView
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    
)
urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('captcha/', CaptchaViewset.as_view(), name='captcha'),
    path('groups/', GroupManagementViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='group-list'),
    
    path('groups/<int:pk>/', GroupManagementViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='group-detail'),
    path('user-to-group/', UserToGroupViewSet.as_view({'post': 'assign_group'}), name='user-to-group'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('permissions/', PermissionListView.as_view(), name='permission-list'),
    path('set-user-permission/', SetUserPermissionView.as_view(), name='set-user-permission'),
    path('permissions-for-user/', PermissionListForUserView.as_view(), name='permissions-for-user'),
]


