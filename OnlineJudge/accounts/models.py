from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class UserMetadata(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='metadata')
    bio = models.TextField(blank=True)
    email = models.EmailField(blank=True)
    linkedin = models.URLField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
