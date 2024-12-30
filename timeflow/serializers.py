from rest_framework import serializers
from .models import UserLoginLog

class UserLoginLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLoginLog
        fields = '__all__'