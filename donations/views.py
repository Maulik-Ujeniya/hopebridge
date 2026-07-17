from django.shortcuts import render, get_object_or_404, redirect
from .models import Donation
from .forms import DonationForm
from django.core.mail import send_mail
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q

def donation_list(request):
    query = request.GET.get('q')
    donation_list = Donation.objects.all()
    if query:
        donation_list = donation_list.filter(Q(donor__name__icontains=query))
    paginator = Paginator(donation_list, 5)
    page_number = request.GET.get('page')
    donations = paginator.get_page(page_number)
    return render(request, 'donations/donation_list.html', {'donations': donations, 'query': query})

def donation_detail(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donations/donation_detail.html', {'donation': donation})

def donation_create(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save()
            send_mail(
                subject='Thank You for Your Donation!',
                message=f'Dear {donation.donor.name},\n\nThank you for your generous donation of {donation.donation_type} to HopeBridge NGO.\n\nYour support helps us continue our mission.\n\nWarm regards,\nHopeBridge Team',
                from_email='noreply@hopebridge.org',
                recipient_list=[donation.donor.email],
                fail_silently=True,
            )
            messages.success(request, f'Donation saved successfully! A thank-you email was sent to {donation.donor.email}.')
            return redirect('donation_list')
    else:
        form = DonationForm()
    return render(request, 'donations/donation_form.html', {'form': form})

def donation_edit(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    if request.method == 'POST':
        form = DonationForm(request.POST, instance=donation)
        if form.is_valid():
            form.save()
            return redirect('donation_detail', donation_id=donation.id)
    else:
        form = DonationForm(instance=donation)
    return render(request, 'donations/donation_form.html', {'form': form})

def donation_delete(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    if request.method == 'POST':
        donation.delete()
        return redirect('donation_list')
    return render(request, 'donations/donation_confirm_delete.html', {'donation': donation})

def donation_invoice(request, donation_id):
    donation = get_object_or_404(Donation, id=donation_id)
    return render(request, 'donations/donation_invoice.html', {'donation': donation})