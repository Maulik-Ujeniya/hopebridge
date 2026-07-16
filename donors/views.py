from django.shortcuts import get_object_or_404, render
from .models import Donor

# Create your views here.

def donor_list(request):
    donors = Donor.objects.all()
    return render(request, 'donors/donor_List.html',{'donors': donors}) 

def donor_detail(request, donor_id):
    donor = get_object_or_404(Donor, id=donor_id)
    donations = donor.donation_set.all()
    return render(request, 'donors/donor_detail.html', {'donor': donor, 'donations': donations})

