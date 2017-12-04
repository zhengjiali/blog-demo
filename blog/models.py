from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class log(models.Model):
	positionId = models.Index()
	positionName = models.CharField(max_length=128)
	salary=models.CharField(max_length=128)
	positionAdvantage = models.CharField(max_length=128)
	positionLables = models.CharField(max_length=128)