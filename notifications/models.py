from django.db import models
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


class Notification(models.Model):
    """In-app notification for users with email support."""
    TYPE_CHOICES = [
        ('donation_success', 'Donation Successful'),
        ('allocation_updated', 'Allocation Updated'),
        ('volunteer_approved', 'Volunteer Approved'),
        ('volunteer_assigned', 'Volunteer Assigned'),
        ('drive_completed', 'Drive Completed'),
        ('announcement', 'Announcement'),
        ('password_changed', 'Password Changed'),
        ('profile_updated', 'Profile Updated'),
        ('system_alert', 'System Alert'),
    ]

    CATEGORY_CHOICES = [
        ('donation', 'Donation'),
        ('volunteer', 'Volunteer'),
        ('admin', 'Admin'),
        ('security', 'Security'),
        ('general', 'General'),
        ('announcement', 'Announcements'),
    ]

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_notifications'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    notification_type = models.CharField(max_length=30, choices=TYPE_CHOICES, default='system_alert')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    link = models.URLField(blank=True, help_text='URL to open on click')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_via_email = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} → {self.recipient.email}"
        
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Optionally trigger email dispatch if this is a critical new notification
        # This is a naive implementation; normally this goes to a Celery task
        if is_new and not self.sent_via_email:
            # We can map specific types that require emails
            email_types = [
                'donation_success', 'volunteer_approved', 
                'announcement', 'volunteer_assigned', 
                'password_changed', 'profile_updated', 'system_alert'
            ]
            if self.notification_type in email_types:
                self.dispatch_email()
                
    def dispatch_email(self):
        """Send an email to the recipient."""
        try:
            send_mail(
                subject=f"HopeBridge: {self.title}",
                message=self.message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.recipient.email],
                fail_silently=False,
            )
            self.sent_via_email = True
            self.save(update_fields=['sent_via_email'])
        except Exception as e:
            print(f"Email failed to send for Notification {self.id}: {e}")
