from django.db import models
from volunteers.models import Volunteer

# Create your models here.

class Event(models.Model):
    name = models.CharField(max_length=200)
    dscription = models.TextField(blank=True)
    date = models.DateField()
    budget_allocated = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    budget_used = models.DecimalField(max_digits=10,decimal_places=2,default=0)
    volunteers = models.ManyToManyField(Volunteer, blank=True) 

    def __str__(self):
        return self.name
