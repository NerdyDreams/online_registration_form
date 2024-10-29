from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from datetime import date
import re

def validate_phone_number(value):
    if not re.match(r'^\d{11}$', value):
        raise ValidationError('Phone number must be exactly 11 digits.')

def validate_email_domain(value):
    allowed_domains = ['gmail.com', 'yahoo.com', 'outlook.com']
    domain = value.split('@')[1].lower()
    if domain not in allowed_domains:
        raise ValidationError('Email domain not allowed. Use Gmail, Yahoo, or Outlook.')

def validate_age(value):
    today = date.today()
    age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
    if age < 18:
        raise ValidationError('Must be at least 18 years old.')

class User(AbstractUser):
    # Add related_name to resolve clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set'  # Changed from user_set
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set'  # Changed from user_set
    )
    
    email = models.EmailField(
        unique=True,
        validators=[validate_email_domain]
    )
    phone_number = models.CharField(
        max_length=11,
        validators=[validate_phone_number]
    )
    date_of_birth = models.DateField(
        validators=[validate_age]
    )
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        self.first_name = self.first_name.capitalize()
        self.last_name = self.last_name.capitalize()
        super().save(*args, **kwargs)

    class Meta:
        # Add swappable definition to properly handle user model swapping
        swappable = 'AUTH_USER_MODEL'

