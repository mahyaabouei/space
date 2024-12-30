from rest_framework import serializers
from .models import Announcement , ShortCut 

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = '__all__'

class ShortCutSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShortCut
        fields = '__all__'

