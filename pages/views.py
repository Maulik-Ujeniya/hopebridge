from django.shortcuts import render
from django.db.models import Sum, Count
import logging


logger = logging.getLogger(__name__)


def home(request):
    """Landing page with NGO overview and statistics."""
    context = {
        'page_title': 'HopeBridge — Building Bridges of Hope',
    }

    # Try to load stats if models exist
    try:
        from donations.models import Donation
        from drives.models import Drive
        from accounts.models import CustomUser

        context['total_donations'] = Donation.objects.filter(
            payment_status='completed'
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_donors'] = CustomUser.objects.filter(role='donor').count()
        context['total_volunteers'] = CustomUser.objects.filter(role='volunteer').count()
        context['active_drives'] = Drive.objects.filter(status='active').count()
        context['completed_drives'] = Drive.objects.filter(status='completed').count()

        if request.user.is_authenticated:
            context['my_donations'] = Donation.objects.filter(
                donor=request.user, payment_status='completed'
            ).aggregate(Sum('amount'))['amount__sum'] or 0
            
            try:
                from volunteers.models import VolunteerProfile
                from drives.models import DriveVolunteer
                context['active_volunteer_drives'] = DriveVolunteer.objects.filter(
                    volunteer=request.user, status='active'
                ).count()
                
                prof = VolunteerProfile.objects.get(user=request.user)
                context['total_volunteer_hours'] = prof.total_hours_worked
            except Exception:
                context['active_volunteer_drives'] = 0
                context['total_volunteer_hours'] = 0
                
            from drives.models import DriveUpdate
            context['announcements'] = DriveUpdate.objects.all().order_by('-posted_at')[:5]
            
            context['upcoming_drives'] = Drive.objects.filter(
                status__in=['planning', 'active']
            ).order_by('start_date')[:3]

    except Exception:
        logger.exception('Failed to build home page statistics')
        context['total_donations'] = 0
        context['total_donors'] = 0
        context['total_volunteers'] = 0
        context['active_drives'] = 0
        context['completed_drives'] = 0

    return render(request, 'pages/home.html', context)


def about(request):
    """About Us page."""
    return render(request, 'pages/about.html', {'page_title': 'About Us — HopeBridge'})


def our_work(request):
    """Our Work page — all categories."""
    return render(request, 'pages/our_work.html', {'page_title': 'Our Work — HopeBridge'})


def gallery(request):
    """Photo gallery page."""
    return render(request, 'pages/gallery.html', {'page_title': 'Gallery — HopeBridge'})


def contact(request):
    """Contact Us page."""
    if request.method == 'POST':
        from django.contrib import messages
        messages.success(request, 'Thank you for reaching out! We will get back to you soon.')
    return render(request, 'pages/contact.html', {'page_title': 'Contact Us — HopeBridge'})


def terms(request):
    """Terms & Conditions page."""
    return render(request, 'pages/terms.html', {'page_title': 'Terms & Conditions — HopeBridge'})


def privacy(request):
    """Privacy Policy page."""
    return render(request, 'pages/privacy.html', {'page_title': 'Privacy Policy — HopeBridge'})
