from django.shortcuts import render
from .models import Program
# Create your views here.
def program_list(request):
    programs = Program.objects.all()
    return render(request, 'programs/program_list.html', {'programs': programs})