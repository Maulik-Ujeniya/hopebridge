from django import forms
from .models import Event


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'name',
            'description',
            'cover_image',
            'event_type',
            'date',
            'start_time',
            'end_time',
            'location',
            'city',
            'budget_allocated',
            'budget_used',
            'max_participants',
            'status',
            'organizer',
            'linked_drive',
            'volunteers',
        ]