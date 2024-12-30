from rest_framework.permissions import BasePermission
from stock_affairs.models import Shareholders, Precedence, Underwriting, UnusedPrecedenceProcess

class IsShareholder(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        shareholder = Shareholders.objects.filter(user=request.user)
        return shareholder.exists()
        
    @property
    def get_permission_name(self):
        return "shareholder"
    
    def get_permission_data(self, request, view):
        has_perm = self.has_permission(request, view)
        if has_perm:
            return {
                "name": self.get_permission_name,
                "has_permission": True,
                "codename": self.get_permission_name
            }
        return None


class IsPrecedence(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        precedence = Precedence.objects.filter(user=request.user)
        return precedence.exists()


    @property
    def get_permission_name(self):
        return "precedence"

    def get_permission_data(self, request, view):
        has_perm = self.has_permission(request, view)
        if has_perm:
            return {
                "name": self.get_permission_name,
                "has_permission": True,
                "codename": self.get_permission_name
            }
        return None

class IsUnderwriting(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        underwriting = Underwriting.objects.filter(
            requested_amount__gt=0
        )
        return underwriting.exists()


    @property
    def get_permission_name(self):
        return "underwriting"

    def get_permission_data(self, request, view):
        has_perm = self.has_permission(request, view)
        if has_perm:
            return {
                "name": self.get_permission_name,
                "has_permission": True,
                "codename": self.get_permission_name
            }
        return None

class IsUnusedPrecedenceProcess(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_staff:
            return True
        unused_precedence_process = UnusedPrecedenceProcess.objects.filter(is_active=True)
        return unused_precedence_process.exists()


    @property
    def get_permission_name(self):
        return "unused_precedence_process"
    
    def get_permission_data(self, request, view):
        has_perm = self.has_permission(request, view)
        if has_perm:
            return {
                "name": self.get_permission_name,
                "has_permission": True,
                "codename": self.get_permission_name
            }
        return None
