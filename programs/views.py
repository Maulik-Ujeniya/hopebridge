from django.shortcuts import render, get_object_or_404
from .models import Program
# Create your views here.

def program_list(request):
    programs = Program.objects.all()
    return render(request, 'programs/program_list.html', {'programs': programs})

def program_detail(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    return render(request, 'programs/program_detail.html', {'program': program})