from django.shortcuts import render, get_object_or_404, redirect
from .models import Program
from .forms import ProgramForm
from django.core.paginator import Paginator
from django.db.models import Q

def program_list(request):
    programs = Program.objects.all()
    return render(request, 'programs/program_list.html', {'programs': programs})

def program_detail(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    return render(request, 'programs/program_detail.html', {'program': program})

def program_create(request):
    if request.method == 'POST':
        form = ProgramForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('program_list')
    else:
        form = ProgramForm()
    return render(request, 'programs/program_form.html', {'form': form})

def program_edit(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    if request.method == 'POST':
        form = ProgramForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            return redirect('program_detail', program_id=program.id)
    else:
        form = ProgramForm(instance=program)
    return render(request, 'programs/program_form.html', {'form': form})

def program_delete(request, program_id):
    program = get_object_or_404(Program, id=program_id)
    if request.method == 'POST':
        program.delete()
        return redirect('program_list')
    return render(request, 'programs/program_confirm_delete.html', {'program': program})

def program_list(request):
    program_list = Program.objects.all()
    paginator = Paginator(program_list, 5)
    page_number = request.GET.get('page')
    programs = paginator.get_page(page_number)
    return render(request, 'programs/program_list.html', {'programs': programs})

def program_list(request):
    query = request.GET.get('q')
    program_list = Program.objects.all()
    if query:
        program_list = program_list.filter(Q(name__icontains=query))
    paginator = Paginator(program_list, 5)
    page_number = request.GET.get('page')
    programs = paginator.get_page(page_number)
    return render(request, 'programs/program_list.html', {'programs': programs, 'query': query})