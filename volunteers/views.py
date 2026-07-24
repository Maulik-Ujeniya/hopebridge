from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum

from .models import VolunteerProfile, VolunteerWorkLog, VolunteerCertificate
from drives.models import Drive, DriveVolunteer
from events.models import Event, EventRegistration
from notifications.models import Notification


@login_required
def volunteer_dashboard(request):
    """Volunteer Dashboard showing logged hours, campaigns, work log list."""
    profile, _ = VolunteerProfile.objects.get_or_create(user=request.user)
    
    # Active assignments
    assigned_drives = DriveVolunteer.objects.filter(volunteer=request.user, status='active')
    
    # Work logs
    work_logs = VolunteerWorkLog.objects.filter(volunteer=request.user).order_by('-date')[:5]
    
    # Aggregated hours
    total_hours = VolunteerWorkLog.objects.filter(volunteer=request.user, verified=True).aggregate(
        Sum('hours_worked')
    )['hours_worked__sum'] or 0
    
    # Update profile hours just in case
    if total_hours != profile.total_hours_worked:
        profile.total_hours_worked = total_hours
        profile.save()

    # Certificates
    certificates_count = VolunteerCertificate.objects.filter(volunteer=request.user).count()
    
    # Notifications
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:5]
    
    # Upcoming Events
    upcoming_events = Event.objects.filter(status='upcoming').order_by('date')[:3]
    
    # Applications (Pending Drives)
    pending_applications = DriveVolunteer.objects.filter(volunteer=request.user, status='pending')

    return render(request, 'volunteers/dashboard.html', {
        'profile': profile,
        'work_logs': work_logs,
        'total_hours': total_hours,
        'assigned_drives': assigned_drives,
        'pending_applications': pending_applications,
        'certificates_count': certificates_count,
        'notifications': notifications,
        'upcoming_events': upcoming_events,
    })


@login_required
def log_work(request):
    """View to log daily work hours for assigned drives."""
    profile, _ = VolunteerProfile.objects.get_or_create(user=request.user)
    assigned_drives = DriveVolunteer.objects.filter(volunteer=request.user, status='active')

    if not assigned_drives.exists():
        messages.warning(request, "You must join a drive before logging volunteer hours.")
        return redirect('drives:drive_list')

    if request.method == 'POST':
        drive_id = request.POST.get('drive_id')
        date_str = request.POST.get('date')
        hours = request.POST.get('hours')
        description = request.POST.get('description')

        try:
            drive = Drive.objects.get(id=drive_id)
            DriveVolunteer.objects.get(drive=drive, volunteer=request.user, status='active')
            work_date = timezone.datetime.strptime(date_str, "%Y-%m-%d").date()

            VolunteerWorkLog.objects.create(
                volunteer=request.user,
                drive=drive,
                date=work_date,
                hours_worked=hours,
                work_description=description,
                verified=False
            )

            messages.success(request, "Work hours logged successfully! Pending manager verification.")
            return redirect('volunteers:volunteer_dashboard')
        except Exception as e:
            messages.error(request, f"Error logging hours: {str(e)}")

    return render(request, 'volunteers/log_work.html', {
        'profile': profile,
        'assigned_drives': assigned_drives,
        'today': timezone.now().date().strftime("%Y-%m-%d"),
    })


@login_required
def profile_update(request):
    """Update volunteer extended profile fields."""
    profile, _ = VolunteerProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        profile.languages = request.POST.get('languages', '')
        profile.experience = request.POST.get('experience', '')
        profile.emergency_contact = request.POST.get('emergency_contact', '')
        profile.motivation = request.POST.get('motivation', '')
        profile.availability = request.POST.get('availability', 'flexible')
        
        # Save interests as a list from comma-separated string
        interests_str = request.POST.get('interests', '')
        profile.interests = [i.strip() for i in interests_str.split(',') if i.strip()]
        
        profile.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('volunteers:profile_update')
        
    return render(request, 'volunteers/profile.html', {
        'profile': profile,
        'interests_str': ', '.join(profile.interests) if profile.interests else ''
    })


@login_required
def volunteer_history(request):
    """View volunteer history: past drives, attendance, hours."""
    profile, _ = VolunteerProfile.objects.get_or_create(user=request.user)
    work_logs = VolunteerWorkLog.objects.filter(volunteer=request.user).order_by('-date')
    completed_drives = DriveVolunteer.objects.filter(volunteer=request.user, status='completed')
    
    return render(request, 'volunteers/history.html', {
        'profile': profile,
        'work_logs': work_logs,
        'completed_drives': completed_drives,
    })


@login_required
def volunteer_certificates(request):
    """View and download certificates."""
    profile, _ = VolunteerProfile.objects.get_or_create(user=request.user)
    certificates = VolunteerCertificate.objects.filter(volunteer=request.user).order_by('-issue_date')
    
    return render(request, 'volunteers/certificates.html', {
        'profile': profile,
        'certificates': certificates,
    })


@login_required
def volunteer_calendar(request):
    """Calendar view for events and drives."""
    profile, _ = VolunteerProfile.objects.get_or_create(user=request.user)
    # Active assignments
    assigned_drives = DriveVolunteer.objects.filter(volunteer=request.user, status='active')
    upcoming_events = Event.objects.filter(status='upcoming').order_by('date')
    
    return render(request, 'volunteers/calendar.html', {
        'profile': profile,
        'assigned_drives': assigned_drives,
        'upcoming_events': upcoming_events,
    })


@login_required
def apply_for_drive(request, drive_id):
    """Apply to volunteer for a drive."""
    drive = get_object_or_404(Drive, id=drive_id)
    
    if request.method == 'POST':
        # Check if already applied or joined
        assoc, created = DriveVolunteer.objects.get_or_create(
            drive=drive,
            volunteer=request.user,
            defaults={'status': 'pending', 'role_in_drive': 'member'}
        )
        
        if created:
            messages.success(request, f"Successfully applied for {drive.title}! Your application is pending review.")
            
            # Create a notification for the user
            Notification.objects.create(
                recipient=request.user,
                title="Application Submitted",
                message=f"Your application for {drive.title} has been submitted successfully.",
                notification_type='assignment'
            )
        else:
            messages.info(request, f"You have already applied or joined {drive.title}. Status: {assoc.status}.")
            
    return redirect('drives:drive_detail', pk=drive.id)