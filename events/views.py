from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import Event, EventRegistration


def event_list(request):
    """List all events, sorted by upcoming first."""
    events = Event.objects.exclude(status='cancelled').order_by('date')
    return render(request, 'events/event_list.html', {
        'events': events,
        'today': timezone.now().date(),
    })


def event_detail(request, event_id):
    """Detail view of a single event."""
    event = get_object_or_404(Event, id=event_id)
    registrations = event.registrations.all()

    is_registered = False
    if request.user.is_authenticated:
        is_registered = EventRegistration.objects.filter(event=event, user=request.user).exists()

    return render(request, 'events/event_detail.html', {
        'event': event,
        'registrations': registrations,
        'is_registered': is_registered,
    })


@login_required
def register_event(request, event_id):
    """Register logged-in user for an event."""
    event = get_object_or_404(Event, id=event_id)

    if event.status == 'cancelled' or event.date < timezone.now().date():
        messages.error(request, "This event is no longer open for registration.")
        return redirect('events:event_detail', event_id=event.id)

    # Check capacity
    if event.max_participants > 0 and event.registrations.count() >= event.max_participants:
        messages.error(request, "Sorry, this event has reached maximum capacity.")
        return redirect('events:event_detail', event_id=event.id)

    registration, created = EventRegistration.objects.get_or_create(
        event=event,
        user=request.user
    )

    if created:
        messages.success(request, f"You have successfully registered for {event.name}!")
        # Create notification
        from notifications.models import Notification
        Notification.objects.create(
            recipient=request.user,
            title="🎪 Registered for Event",
            message=f"You successfully registered for {event.name}. Date: {event.date}.",
            notification_type='event',
            link=f"/events/{event.id}/"
        )
    else:
        messages.info(request, "You are already registered for this event.")

    return redirect('events:event_detail', event_id=event.id)
