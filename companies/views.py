from .models import Company
from .serializers import CompanySerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
class CompanyViewset(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAdminUser]
        elif not self.request.user.is_staff:
            self.queryset = Company.objects.filter(user=self.request.user)
        return super().get_permissions()


