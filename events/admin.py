from django.contrib import admin
from .models import Event, EventImage, EventRegistration

admin.site.register(Event)
admin.site.register(EventImage)
admin.site.register(EventRegistration)
