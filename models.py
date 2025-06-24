from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Food(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    calories = models.PositiveBigIntegerField()
    date_added = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.name}- {self.calories}"