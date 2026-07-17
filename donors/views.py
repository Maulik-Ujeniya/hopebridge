from django.shortcuts import render, get_object_or_404, redirect
from .models import Donor
from .forms import DonorForm
from django.core.paginator import Paginator
from django.core.paginator import Paginator
from django.db.models import Q
# Create your views here.

def donor_list(request):
    donors = Donor.objects.all()
    return render(request, 'donors/donor_List.html',{'donors': donors}) 

def donor_detail(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    donations = donor.donation_set.all()
    return render(request, 'donors/donor_detail.html', {'donor': donor, 'donations': donations})

def donor_create(request):
    if request.method == 'POST':
        form = DonorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('donor_list')
    else:
        form = DonorForm()
    return render(request, 'donors/donor_form.html', {'form': form})


def donor_edit(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    if request.method == 'POST':
        form = DonorForm(request.POST, instance=donor)
        if form.is_valid():
            form.save()
            return redirect('donor_detail', donor_id=donor.id)
    else:
        form = DonorForm(instance=donor)
    return render(request, 'donors/donor_form.html', {'form': form})

def donor_delete(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    if request.method == 'POST':
        donor.delete()
        return redirect('donor_list')
    return render(request, 'donors/donor_confirm_delete.html', {'donor': donor})

def donor_list(request):
    donor_list = Donor.objects.all()
    paginator = Paginator(donor_list, 5)  # 5 donors per page
    page_number = request.GET.get('page')
    donors = paginator.get_page(page_number)
    return render(request, 'donors/donor_list.html', {'donors': donors})

def donor_list(request):
    query = request.GET.get('q')
    donor_list = Donor.objects.all()
    if query:
        donor_list = donor_list.filter(Q(name__icontains=query) | Q(email__icontains=query))
    paginator = Paginator(donor_list, 5)
    page_number = request.GET.get('page')
    donors = paginator.get_page(page_number)
    return render(request, 'donors/donor_list.html', {'donors': donors, 'query': query})