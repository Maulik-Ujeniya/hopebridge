from django import forms
from .models import Program


class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = [
            'name',
            'category',
            'description',
            'cover_image',
            'status',
            'start_date',
            'end_date',
            'total_budget',
            'spent_budget',
            'target_impact',
            'actual_impact',
            'sponsors',
            'program_manager',
            'cities_covered',
            'beneficiaries_count',
        ]