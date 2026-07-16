from django import forms
from .models import Program

class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'program_type', 'description', 'start_date', 'end_date', 'sponsor']