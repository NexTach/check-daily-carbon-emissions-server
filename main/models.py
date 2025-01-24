from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)
    totalCarbonSaved = models.FloatField(default=0)
    profileImage = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s profile"

class DailyRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    
    waterConsumed = models.FloatField(default=0)
    showerTime = models.IntegerField(default=0)
    
    carUsageDistance = models.FloatField(default=0)
    carUsageTime = models.IntegerField(default=0)
    publicTransportTime = models.IntegerField(default=0)
    walkingSteps = models.IntegerField(default=0)
    
    electricityUsage = models.FloatField(default=0)
    
    videoWatchingTime = models.IntegerField(default=0)
    internetUsage = models.FloatField(default=0)
    
    totalCarbonEmission = models.FloatField(default=0)
    carbonSaved = models.FloatField(default=0)
    treesNeeded = models.FloatField(default=0)

    class Meta:
        unique_together = ['user', 'date']

class Reward(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    pointsRequired = models.IntegerField()
    imageUrl = models.URLField()
