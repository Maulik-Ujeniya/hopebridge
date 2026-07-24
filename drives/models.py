from django.db import models
from django.conf import settings


class DriveCategory(models.Model):
    """Categories for drives — Food, Clothing, Education, etc."""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, help_text='Lucide icon name')
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6C63FF', help_text='Hex color for UI')

    class Meta:
        verbose_name_plural = 'Drive Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Drive(models.Model):
    """A drive/campaign organized by the NGO."""
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    title = models.CharField(max_length=200)
    category = models.ForeignKey(DriveCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='drives')
    description = models.TextField()
    cover_image = models.FileField(upload_to='drives/covers/%Y/%m/', blank=True, null=True)
    location_city = models.CharField(max_length=100)
    location_area = models.CharField(max_length=200, blank=True)
    location_address = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    budget_allocated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_used = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_beneficiaries = models.PositiveIntegerField(default=0)
    actual_beneficiaries = models.PositiveIntegerField(default=0)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_drives')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_drives')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def budget_pending(self):
        return self.budget_allocated - self.budget_used

    @property
    def progress_percentage(self):
        if self.target_beneficiaries > 0:
            return min(int((self.actual_beneficiaries / self.target_beneficiaries) * 100), 100)
        return 0


class DriveImage(models.Model):
    """Gallery images for a drive."""
    drive = models.ForeignKey(Drive, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.FileField(upload_to='drives/gallery/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.drive.title}"


class DriveVolunteer(models.Model):
    """Tracks volunteer participation in a drive."""
    ROLE_CHOICES = [
        ('lead', 'Lead'),
        ('member', 'Member'),
        ('coordinator', 'Coordinator'),
    ]
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]

    drive = models.ForeignKey(Drive, on_delete=models.CASCADE, related_name='drive_volunteers')
    volunteer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='drive_participations')
    role_in_drive = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    hours_per_day = models.PositiveIntegerField(default=0)
    total_hours_worked = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    joined_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ['drive', 'volunteer']

    def __str__(self):
        return f"{self.volunteer} — {self.drive.title}"


class DriveUpdate(models.Model):
    """Status updates posted to a drive."""
    drive = models.ForeignKey(Drive, on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.FileField(upload_to='drives/updates/%Y/%m/', blank=True, null=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.title} — {self.drive.title}"
