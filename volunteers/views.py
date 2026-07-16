from django.shortcuts import render, get_object_or_404
from .models import Volunteer
# Create your views here.

def volunteer_list(request):
    volunteers = Volunteer.objects.all()
    return render(request, 'volunteers/volunteer_list.html', {'volunteers': volunteers})

def volunteer_detail(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    events = volunteer.event_set.all()
    return render(request, 'volunteers/volunteer_detail.html', {'volunteer': volunteer, 'events': events})