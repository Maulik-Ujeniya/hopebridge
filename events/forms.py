from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['name', 'dscription', 'date', 'budget_allocated', 'budget_used', 'volunteers']