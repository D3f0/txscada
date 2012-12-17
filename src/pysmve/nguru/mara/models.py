from django.db import models

# Create your models here.
class Profile(models.Model):
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    
    
class COMaster(models.Model):
    profile = models.ForeignKey(Profile)
    ip_address = models.IPAddressField()
    
    
    