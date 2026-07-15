

from django.db import models
from donors.models import Donor

# Create your models here.

class Program(models.Model):
    PROGRAM_TYPES = [
        ('relief', 'Relief Program'),
        ('education', 'Education Sponsorship'),
        ('food_drive', 'Food Drive'),
        ('book_donation', 'Book Donation'),
    ]

    name = models.CharField(max_length=200)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPES)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    sponsor = models.ForeignKey(Donor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name