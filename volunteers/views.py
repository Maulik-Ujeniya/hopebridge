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

def volunteer_edit(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    if request.method == 'POST':
        form = VolunteerForm(request.POST, instance=volunteer)
        if form.is_valid():
            form.save()
            return redirect('volunteer_detail', volunteer_id=volunteer.id)
    else:
        form = VolunteerForm(instance=volunteer)
    return render(request, 'volunteers/volunteer_form.html', {'form': form})

def volunteer_delete(request, volunteer_id):
    volunteer = get_object_or_404(Volunteer, id=volunteer_id)
    if request.method == 'POST':
        volunteer.delete()
        return redirect('volunteer_list')
    return render(request, 'volunteers/volunteer_confirm_delete.html', {'volunteer': volunteer})