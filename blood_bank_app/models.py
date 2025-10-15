from django.db import models

# Create your models here.
from django.contrib.auth.models import User
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('donor', 'Donor'),
        ('patient', 'Patient'),
        ('hospital','Hospital'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='donor')

    def __str__(self):
        return f"{self.user} ({self.role})"