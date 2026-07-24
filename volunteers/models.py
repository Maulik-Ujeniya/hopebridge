from django.db import models
from django.conf import settings


class VolunteerProfile(models.Model):
    """Extended volunteer profile data — linked to CustomUser with role='volunteer'."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='volunteer_profile')
    skills = models.JSONField(default=list, blank=True)
    availability = models.CharField(
        max_length=20,
        choices=[
            ('weekdays', 'Weekdays'),
            ('weekends', 'Weekends'),
            ('both', 'Both'),
            ('flexible', 'Flexible'),
        ],
        default='flexible'
    )
    hours_per_week = models.PositiveIntegerField(default=0)
    total_hours_worked = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    drives_completed = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    bio = models.TextField(blank=True)
    certifications = models.TextField(blank=True)
    
    # Extended profile fields
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('rejected', 'Rejected'),
        ],
        default='pending'
    )
    languages = models.CharField(max_length=200, blank=True, help_text="Comma-separated list of languages")
    experience = models.TextField(blank=True, help_text="Previous volunteer experience")
    emergency_contact = models.CharField(max_length=100, blank=True)
    interests = models.JSONField(default=list, blank=True, help_text="List of interests")
    motivation = models.TextField(blank=True, help_text="Why do you want to volunteer?")
    reward_points = models.PositiveIntegerField(default=0, help_text="Gamification points")
    def __str__(self):
        return f"Volunteer: {self.user.get_full_name()}"


class VolunteerWorkLog(models.Model):
    """Tracks daily work logged by volunteers."""
    volunteer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_logs')
    drive = models.ForeignKey('drives.Drive', on_delete=models.CASCADE, related_name='work_logs')
    date = models.DateField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    work_description = models.TextField()
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_logs')
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.volunteer} — {self.drive.title} ({self.date})"


class VolunteerCertificate(models.Model):
    """Certificates issued to volunteers for completing drives or events."""
    volunteer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    issue_date = models.DateField(auto_now_add=True)
    drive = models.ForeignKey('drives.Drive', on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_certificates')
    event = models.ForeignKey('events.Event', on_delete=models.SET_NULL, null=True, blank=True, related_name='issued_certificates')
    certificate_file = models.FileField(upload_to='certificates/%Y/%m/', blank=True, null=True)

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"Certificate: {self.title} for {self.volunteer.get_full_name()}"
