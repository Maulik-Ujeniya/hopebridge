from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """
    Custom User model for HopeBridge.
    Uses email as the primary login identifier.
    """

    ROLE_CHOICES = [
        ('donor', 'Donor'),
        ('volunteer', 'Volunteer'),
        ('manager', 'Drive Manager'),
        ('admin', 'Admin'),
    ]

    # Profile fields
    profile_picture = models.FileField(
        upload_to='profiles/%Y/%m/',
        blank=True,
        null=True,
        help_text='Upload your profile picture'
    )
    phone = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    full_address = models.TextField(blank=True)

    # Role & status
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='donor')
    is_profile_complete = models.BooleanField(default=False)
    last_active = models.DateTimeField(auto_now=True)

    # Email as primary identifier
    email = models.EmailField(unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return self.get_full_name() or self.email

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return '/static/images/default-avatar.svg'


class UserPreference(models.Model):
    """
    Stores the user's onboarding preferences —
    filled during the 4-step registration flow.
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='preferences'
    )

    # Step 1: Contribution type
    wants_to_donate = models.BooleanField(default=False)
    wants_to_volunteer = models.BooleanField(default=False)
    wants_to_manage = models.BooleanField(default=False)

    # Step 2: Role details
    preferred_role = models.CharField(max_length=50, blank=True)
    experience_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('experienced', 'Experienced'),
        ],
        default='beginner'
    )

    # Step 3: Detailed preferences
    preferred_categories = models.JSONField(
        default=list,
        blank=True,
        help_text='List of preferred drive categories'
    )
    skills = models.TextField(blank=True, help_text='Your skills and expertise')
    availability_hours = models.PositiveIntegerField(
        default=0,
        help_text='Hours per week you can contribute'
    )
    availability_days = models.CharField(
        max_length=20,
        choices=[
            ('weekdays', 'Weekdays'),
            ('weekends', 'Weekends'),
            ('both', 'Both'),
            ('flexible', 'Flexible'),
        ],
        default='flexible'
    )

    # Step 4: Goals & motivation
    motivation = models.TextField(blank=True, help_text='What motivates you to join HopeBridge?')
    future_goals = models.TextField(blank=True, help_text='Your goals with HopeBridge')
    how_did_you_hear = models.CharField(max_length=100, blank=True)
    agree_to_terms = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Preference'
        verbose_name_plural = 'User Preferences'

    def __str__(self):
        return f"Preferences for {self.user.email}"
