from django.shortcuts import render
from django.db.models import Sum,Count
from donors.models import Donor
from volunteers.models import Volunteer
from donations.models import Donation
from events.models import Event
from programs.models import Program

def home(request):
    total_donors = Donor.objects.count()
    total_volunteers = Volunteer.objects.count()
    total_events = Event.objects.count()
    total_programs = Program.objects.count()

    total_money_donated = Donation.objects.filter(donation_type='money').aggregate(Sum('amount'))['amount__sum'] or 0
    total_donations_count = Donation.objects.count()
    total_volunteer_hours = Volunteer.objects.aggregate(Sum('hours_contributed'))['hours_contributed__sum'] or 0

    context = {
        'total_donors': total_donors,
        'total_volunteers': total_volunteers,
        'total_events': total_events,
        'total_programs': total_programs,
        'total_money_donated': total_money_donated,
        'total_donations_count': total_donations_count,
        'total_volunteer_hours': total_volunteer_hours,
    }
    return render(request, 'home.html', context)