from django.db import models
from donors.models import Donor
# Create your models here.

class Donation(models.Model):
    DONATION_TYPE = [
        ('money','Money'),
        ('food','Food Packets'),
        ('clothes','Clothes'),
        ('books','Books'),
    ]

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE)
    donation_type = models.CharField(max_length=20 ,choices=DONATION_TYPE)
    amount =models.DecimalField(max_digits=10,decimal_places=2,null=True,blank=True)
    quantity = models.PositiveIntegerField(null=True,blank=True)
    date_donated = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.name} - {self.donation_type}"
