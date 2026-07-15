from django.db import models

# Create your models here.
class Donor(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    total_donated = models.DecimalField(max_digits=10 , decimal_places=2 , default=0)
    joined_date = models.DateField(auto_now_add=True)

def __str__(self):
    return self.name

