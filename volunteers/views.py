from django.shortcuts import render
from .models import Volunteer
# Create your views here.

def volunteer_list(request):
    volunteers = Volunteer.objects.all()
    return render(request, 'volunteers/volunteer_list.html', {'volunteers': volunteers})
