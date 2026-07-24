from django import forms
from .models import VolunteerProfile


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = VolunteerProfile
        fields = [
            'skills',
            'availability',
            'hours_per_week',
            'bio',
            'certifications',
        ]