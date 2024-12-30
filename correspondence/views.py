from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated , IsAdminUser
from .permissions import IsSenderCorrespondence, IsReceiverCorrespondence, IsOpenCorrespondence
from .models import Correspondence
from .serializers import CorrespondenceSerializer
from .number_generator import CorrespondenceNumberGenerator
from django.db.models import Q
from positions.models import Position
from django.core.exceptions import ValidationError

class CorrespondencerViewset(viewsets.ModelViewSet):
    queryset = Correspondence.objects.all()
    serializer_class = CorrespondenceSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            if self.request.user.is_staff:
                self.permission_classes = [IsAuthenticated]
            else:
                self.permission_classes = [IsReceiverCorrespondence, IsSenderCorrespondence]
        elif self.action == 'create':
            self.permission_classes = [IsAuthenticated, IsAdminUser]
        elif self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [(IsAdminUser | IsSenderCorrespondence) & IsOpenCorrespondence]
        return super().get_permissions()
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Correspondence.objects.all()
        else:
            user_positions = Position.objects.filter(user=self.request.user)
            return Correspondence.objects.filter(
                Q(receiver_internal__in=user_positions) | 
                Q(sender__in=user_positions)
            ).select_related('sender', 'receiver_internal')

    def perform_create(self, serializer):
        sender_position = Position.objects.filter(user=self.request.user).first() # get sender position
        if not sender_position:
            raise ValidationError("کاربر فعلی دارای موقعیت سازمانی نیست")
        
        serializer.save(
            draft=True, 
            number=None,
            sender=sender_position
        )
        
    def perform_update(self, serializer):
        obj = serializer.instance
        if obj.draft:
            number_str, number_obj = CorrespondenceNumberGenerator.generate_number()
            serializer.save(draft=False, number=number_obj)
        else:
            serializer.save()
        


