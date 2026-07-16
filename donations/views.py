from django.shortcuts import render, get_object_or_404, redirect
from .models import Donation
from .forms import DonationForm

def donation_list(request):
    donations = Donation.objects.all()
    return render(request, 'donations/donation_list.html', {'donations': donations})

def donation_detail(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donations/donation_detail.html', {'donation': donation})

def donation_create(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('donation_list')
    else:
        form = DonationForm()
    return render(request, 'donations/donation_form.html', {'form': form})