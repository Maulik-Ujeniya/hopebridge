from django.db import models

# Create your models here.
class volunteer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    hours_contributed = models.PositiveIntegerField(default=0)
    joined_date = models.DateField(auto_now_add=True)

def __str__(self):
    return self.name
