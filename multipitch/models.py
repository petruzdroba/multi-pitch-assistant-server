from django.db import models
from django.contrib.auth.models import AbstractUser

class UserAuth(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

class UserBackup(models.Model):
    user = models.OneToOneField(UserAuth, on_delete=models.CASCADE, related_name="data")
    sqlite_blob = models.BinaryField()
    last_sync= models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Backup for {self.user.username} at {self.last_sync}"
    