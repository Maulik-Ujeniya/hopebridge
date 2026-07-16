from django.shortcuts import render, get_object_or_404, redirect
from .models import Volunteer
from .forms import VolunteerForm

def volunteer_list(request):
    volunteers = Volunteer.objects.all()
    return render(request, 'volunteers/volunteer_list.html', {'volunteers': volunteers})

def volunteer_detail(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    events = volunteer.event_set.all()
    return render(request, 'volunteers/volunteer_detail.html', {'volunteer': volunteer, 'events': events})

def volunteer_create(request):
    if request.method == 'POST':
        form = VolunteerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('volunteer_list')
    else:
        form = VolunteerForm()
    return render(request, 'volunteers/volunteer_form.html', {'form': form})