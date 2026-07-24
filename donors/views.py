from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from .models import Donor
from .forms import DonorForm
from donations.models import Donation
from django.core.paginator import Paginator
from django.db.models import Q

def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.role == 'admin')

@user_passes_test(is_admin)
def donor_list(request):
    query = request.GET.get('q')
    donor_list = Donor.objects.all()
    if query:
        donor_list = donor_list.filter(Q(name__icontains=query) | Q(email__icontains=query))
    paginator = Paginator(donor_list, 5)
    page_number = request.GET.get('page')
    donors = paginator.get_page(page_number)
    return render(request, 'donors/donor_list.html', {'donors': donors, 'query': query})

@user_passes_test(is_admin)
def donor_detail(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    donations = Donation.objects.filter(email=donor.email).order_by('-date_donated')
    return render(request, 'donors/donor_detail.html', {'donor': donor, 'donations': donations})

@user_passes_test(is_admin)
def donor_create(request):
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('donors:donor_list')
    else:
        form = DonorForm()
    return render(request, 'donors/donor_form.html', {'form': form})


@user_passes_test(is_admin)
def donor_edit(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    if request.method == 'POST':
        form = DonorForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            return redirect('donors:donor_detail', donor_id=donor.id)
    else:
        form = DonorForm(instance=donor)
    return render(request, 'donors/donor_form.html', {'form': form})

@user_passes_test(is_admin)
def donor_delete(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    if request.method == 'POST':
        donor.delete()
        return redirect('donors:donor_list')
    return render(request, 'donors/donor_confirm_delete.html', {'donor': donor})