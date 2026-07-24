from django.db import models

class OrganizationSettings(models.Model):
    """Singleton model for NGO Organization Settings."""
    name = models.CharField(max_length=200, default="HopeBridge NGO")
    contact_email = models.EmailField(default="contact@hopebridge.org")
    contact_phone = models.CharField(max_length=20, default="+1 234 567 8900")
    address = models.TextField(blank=True)
    
    # Social Links
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    
    # Tax / Legal Info
    tax_id = models.CharField(max_length=50, blank=True, help_text="e.g. 80G/12A Registration Number")
    legal_name = models.CharField(max_length=200, blank=True)
    
    # Appearance
    logo = models.FileField(upload_to='org_settings/', blank=True, null=True)

    class Meta:
        verbose_name = 'Organization Settings'
        verbose_name_plural = 'Organization Settings'

    def __str__(self):
        return self.name

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj
