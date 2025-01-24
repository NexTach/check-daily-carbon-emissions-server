from rest_framework import serializers
from .models import UserProfile, DailyRecord, Reward

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['points', 'totalCarbonSaved']

class DailyRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyRecord
        fields = (
            'id', 'date', 
            'waterConsumed', 'showerTime',
            'carUsageDistance', 'carUsageTime',
            'publicTransportTime', 'walkingSteps',
            'electricityUsage',
            'videoWatchingTime', 'internetUsage',
            'totalCarbonEmission', 'carbonSaved',
            'treesNeeded'
        )

class RewardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reward
        fields = '__all__' 