from django.shortcuts import render, get_object_or_404
from .models import Donation

def donation_list(request):
    donations = Donation.objects.all()
    return render(request, 'donations/donation_list.html', {'donations': donations})

def donation_detail(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donations/donation_detail.html', {'donation': donation})