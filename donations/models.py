from django.db import models
from django.conf import settings


class Donation(models.Model):
    """Records a donation made to HopeBridge."""
    DONATION_TYPE_CHOICES = [
        ('money', 'Money'),
        ('food', 'Food Packets'),
        ('clothes', 'Clothes'),
        ('books', 'Books'),
        ('other', 'Other'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online Payment'),
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('bank_transfer', 'Bank Transfer'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Donor info (linked to user if authenticated, otherwise stored directly)
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='donations'
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)
    full_address = models.TextField(blank=True)

    # Donation details
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPE_CHOICES, default='money')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    quantity = models.PositiveIntegerField(null=True, blank=True)

    # Payment details
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='online')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=200, blank=True)
    payment_gateway = models.CharField(max_length=20, default='razorpay')
    razorpay_order_id = models.CharField(max_length=200, blank=True)
    razorpay_payment_id = models.CharField(max_length=200, blank=True)
    razorpay_signature = models.CharField(max_length=500, blank=True)

    # Invoice
    invoice_number = models.CharField(max_length=20, unique=True, blank=True)

    # Meta
    notes = models.TextField(blank=True)
    date_donated = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_donated']

    def __str__(self):
        return f"{self.name} — ₹{self.amount} ({self.donation_type})"

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            from django.utils import timezone
            year = timezone.now().year
            last = Donation.objects.filter(
                invoice_number__startswith=f'HB-{year}-'
            ).order_by('-invoice_number').first()
            if last and last.invoice_number:
                try:
                    num = int(last.invoice_number.split('-')[-1]) + 1
                except (ValueError, IndexError):
                    num = 1
            else:
                num = 1
            self.invoice_number = f'HB-{year}-{num:05d}'
        super().save(*args, **kwargs)


class DonationAllocation(models.Model):
    """Tracks how a donation is allocated to drives."""
    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='allocations')
    drive = models.ForeignKey('drives.Drive', on_delete=models.CASCADE, related_name='donation_allocations')
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    used_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    allocated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    allocated_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    @property
    def pending_amount(self):
        return self.allocated_amount - self.used_amount

    def __str__(self):
        return f"₹{self.allocated_amount} → {self.drive.title}"
