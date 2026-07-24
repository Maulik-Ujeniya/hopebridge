from django.shortcuts import render, get_object_or_404
from .models import Program, ProgramCategory


def program_list(request):
    """List all NGO programs grouped by category."""
    categories = ProgramCategory.objects.all()
    programs = Program.objects.exclude(status='completed')
    return render(request, 'programs/program_list.html', {
        'categories': categories,
        'programs': programs,
    })


def program_detail(request, program_id):
    """Detail view for programs including updates timeline and sponsor details."""
    program = get_object_or_404(Program, id=program_id)
    updates = program.updates.all()
    sponsors = program.sponsors.all()
    return render(request, 'programs/program_detail.html', {
        'program': program,
        'updates': updates,
        'sponsors': sponsors,
    })