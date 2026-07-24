from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

from .models import Drive, DriveCategory, DriveVolunteer, DriveUpdate


def drive_list(request):
    """View to list all drives with category and city filtering."""
    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    city = request.GET.get('city', '')

    drives = Drive.objects.exclude(status='cancelled')

    if query:
        drives = drives.filter(Q(title__icontains=query) | Q(description__icontains=query))
    if category_id:
        drives = drives.filter(category_id=category_id)
    if city:
        drives = drives.filter(location_city__icontains=city)

    categories = DriveCategory.objects.all()
    # Distinct cities
    cities = Drive.objects.exclude(location_city='').values_list('location_city', flat=True).distinct()

    return render(request, 'drives/drive_list.html', {
        'drives': drives,
        'categories': categories,
        'cities': cities,
        'query': query,
        'selected_category': category_id,
        'selected_city': city,
    })


def drive_detail(request, drive_id):
    """Detailed view of a single drive."""
    drive = get_object_or_404(Drive, id=drive_id)
    updates = drive.updates.all()
    volunteers = drive.drive_volunteers.filter(status='active')

    # Check if logged-in user is already a volunteer for this drive
    is_joined = False
    if request.user.is_authenticated:
        is_joined = DriveVolunteer.objects.filter(drive=drive, volunteer=request.user, status='active').exists()

    return render(request, 'drives/drive_detail.html', {
        'drive': drive,
        'updates': updates,
        'volunteers': volunteers,
        'is_joined': is_joined,
    })


@login_required
def join_drive(request, drive_id):
    """Endpoint for logged-in users to join a drive."""
    drive = get_object_or_404(Drive, id=drive_id)

    if drive.status != 'active':
        messages.error(request, "This drive is not currently active.")
        return redirect('drives:drive_detail', drive_id=drive.id)

    # Check if already joined
    joined_exists = DriveVolunteer.objects.filter(drive=drive, volunteer=request.user).first()
    if joined_exists:
        if joined_exists.status == 'active':
            messages.info(request, "You are already a volunteer for this drive.")
        else:
            joined_exists.status = 'active'
            joined_exists.save()
            messages.success(request, f"Welcome back! You have successfully joined the drive: {drive.title}.")
    else:
        # Default hours per day from preferences if volunteer
        hours = 2
        if hasattr(request.user, 'preferences'):
            hours = request.user.preferences.availability_hours // 5 or 2

        DriveVolunteer.objects.create(
            drive=drive,
            volunteer=request.user,
            role_in_drive='member',
            hours_per_day=hours,
            status='active'
        )

        # Make sure user role is updated to volunteer if it is currently donor/guest
        if request.user.role == 'donor':
            request.user.role = 'volunteer'
            request.user.save(update_fields=['role'])

        messages.success(request, f"Thank you! You have successfully registered as a volunteer for: {drive.title}.")

    # Create notification
    from notifications.models import Notification
    Notification.objects.create(
        recipient=request.user,
        title="🚗 Joined Drive",
        message=f"You joined the drive: {drive.title}. Get in touch with the manager: {drive.manager}.",
        notification_type='drive',
        link=f"/drives/{drive.id}/"
    )

    return redirect('drives:drive_detail', drive_id=drive.id)
