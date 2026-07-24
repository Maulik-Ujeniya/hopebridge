from django.contrib import admin
from .models import Donation, DonationAllocation

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'name', 'amount', 'donation_type', 'payment_status', 'date_donated']
    list_filter = ['donation_type', 'payment_status', 'payment_method']
    search_fields = ['name', 'email', 'invoice_number']

@admin.register(DonationAllocation)
class DonationAllocationAdmin(admin.ModelAdmin):
    list_display = ['donation', 'drive', 'allocated_amount', 'used_amount', 'allocated_date']
