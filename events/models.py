from django.db import models
from django.conf import settings


class Event(models.Model):
    """An event organized by HopeBridge."""
    TYPE_CHOICES = [
        ('drive', 'Drive Event'),
        ('fundraiser', 'Fundraiser'),
        ('awareness', 'Awareness Campaign'),
        ('celebration', 'Celebration'),
    ]
    STATUS_CHOICES = [
        ('upcoming', 'Upcoming'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image = models.FileField(upload_to='events/covers/%Y/%m/', blank=True, null=True)
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='drive')
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    budget_allocated = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    budget_used = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    max_participants = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='upcoming')
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='organized_events')
    linked_drive = models.ForeignKey('drives.Drive', on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    volunteers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='volunteered_events')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return self.name


class EventImage(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='gallery')
    image = models.FileField(upload_to='events/gallery/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.event.name}"


class EventRegistration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ['event', 'user']

    def __str__(self):
        return f"{self.user} → {self.event.name}"
