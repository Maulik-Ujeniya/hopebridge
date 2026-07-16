from django.shortcuts import render
from .models import Event
# Create your views here.

def event_list(request):
    events = Event.objects.all()
    return render(request, 'events/event_list.html', {'events': events})


