from django.db import models
from django.conf import settings


class ProgramCategory(models.Model):
    """Categories for programs — Health, Education, etc."""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.FileField(upload_to='programs/categories/', blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Program Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Program(models.Model):
    """A long-running program run by HopeBridge."""
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(ProgramCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='programs')
    description = models.TextField(blank=True)
    cover_image = models.FileField(upload_to='programs/covers/%Y/%m/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    total_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    spent_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    target_impact = models.TextField(blank=True)
    actual_impact = models.TextField(blank=True)
    sponsors = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='sponsored_programs')
    program_manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_programs')
    cities_covered = models.JSONField(default=list, blank=True)
    beneficiaries_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class ProgramImage(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='gallery')
    image = models.FileField(upload_to='programs/gallery/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.program.name}"


class ProgramUpdate(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=200)
    update_text = models.TextField()
    image = models.FileField(upload_to='programs/updates/%Y/%m/', blank=True, null=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-posted_at']

    def __str__(self):
        return f"{self.title} — {self.program.name}"