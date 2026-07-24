import csv
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from functools import wraps

from accounts.models import CustomUser
from donations.models import Donation, DonationAllocation
from drives.models import Drive
from events.models import Event
from programs.models import Program
from notifications.models import Notification
from .models import OrganizationSettings


def admin_required(view_func):
    """Decorator to restrict access only to admins."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        is_admin = request.user.is_authenticated and (
            request.user.is_staff or request.user.is_superuser or request.user.role == 'admin'
        )
        if not is_admin:
            messages.error(request, "Access denied. Admin privileges required.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required
@admin_required
def dashboard(request):
    """Custom Admin Dashboard with analytics data."""
    # Overview Stats
    total_raised = Donation.objects.filter(payment_status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
    total_used = DonationAllocation.objects.aggregate(Sum('used_amount'))['used_amount__sum'] or 0
    total_donors = CustomUser.objects.filter(role='donor').count()
    total_volunteers = CustomUser.objects.filter(role='volunteer').count()
    active_drives = Drive.objects.filter(status='active').count()
    active_programs = Program.objects.filter(status='active').count()
    
    today = timezone.now().date()
    today_donations = Donation.objects.filter(payment_status='completed', date_donated__date=today).aggregate(Sum('amount'))['amount__sum'] or 0

    allocated_budget = Drive.objects.aggregate(Sum('budget_allocated'))['budget_allocated__sum'] or 0
    spent_budget = Drive.objects.aggregate(Sum('budget_used'))['budget_used__sum'] or 0

    # Chart Data: Category Breakdown
    donations_by_category = Donation.objects.filter(payment_status='completed').values('donation_type').annotate(total=Sum('amount'))
    category_labels = [item['donation_type'].title() for item in donations_by_category]
    category_data = [float(item['total']) for item in donations_by_category]
    
    # Chart Data: Monthly Donations (Last 6 months)
    monthly_labels = []
    monthly_data = []
    for i in range(5, -1, -1):
        target_month = today.replace(day=1) - timedelta(days=30 * i)
        start_date = target_month.replace(day=1)
        end_date = (start_date + timedelta(days=32)).replace(day=1)
        monthly_labels.append(start_date.strftime("%b %Y"))
        
        sum_amount = Donation.objects.filter(
            payment_status='completed',
            date_donated__gte=start_date,
            date_donated__lt=end_date
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_data.append(float(sum_amount))

    recent_donations = Donation.objects.filter(payment_status='completed').order_by('-date_donated')[:5]
    recent_users = CustomUser.objects.all().order_by('-date_joined')[:5]

    return render(request, 'custom_admin/dashboard.html', {
        'total_raised': total_raised,
        'today_donations': today_donations,
        'total_used': total_used,
        'total_donors': total_donors,
        'total_volunteers': total_volunteers,
        'active_drives': active_drives,
        'active_programs': active_programs,
        'allocated_budget': allocated_budget,
        'spent_budget': spent_budget,
        'recent_donations': recent_donations,
        'recent_users': recent_users,
        'category_labels': category_labels,
        'category_data': category_data,
        'monthly_labels': monthly_labels,
        'monthly_data': monthly_data,
    })


@login_required
@admin_required
def user_list(request):
    """Manage Users."""
    role_filter = request.GET.get('role', '')
    users = CustomUser.objects.all().order_by('-date_joined')

    if role_filter:
        users = users.filter(role=role_filter)

    return render(request, 'custom_admin/user_list.html', {
        'users': users,
        'role_filter': role_filter,
    })


@login_required
@admin_required
def user_detail(request, user_id):
    """Show detailed user info."""
    user_obj = get_object_or_404(CustomUser, id=user_id)
    donations = Donation.objects.filter(donor=user_obj)
    assignments = user_obj.drive_participations.all() if hasattr(user_obj, 'drive_participations') else []
    return render(request, 'custom_admin/user_detail.html', {
        'managed_user': user_obj,
        'donations': donations,
        'assignments': assignments,
    })


@login_required
@admin_required
def toggle_user_status(request, user_id):
    """Activate/Deactivate user."""
    user_obj = get_object_or_404(CustomUser, id=user_id)
    if user_obj == request.user:
        messages.error(request, "You cannot deactivate your own account.")
    else:
        user_obj.is_active = not user_obj.is_active
        user_obj.save()
        status_str = "activated" if user_obj.is_active else "deactivated"
        messages.success(request, f"User {user_obj.email} successfully {status_str}.")
    return redirect('custom_admin:user_list')


@login_required
@admin_required
def assign_role(request, user_id):
    """Assign role to user."""
    if request.method == 'POST':
        user_obj = get_object_or_404(CustomUser, id=user_id)
        role = request.POST.get('role')
        if role in dict(CustomUser.ROLE_CHOICES):
            user_obj.role = role
            user_obj.save()
            messages.success(request, f"Role for {user_obj.email} updated to {role}.")
        else:
            messages.error(request, "Invalid role selected.")
    return redirect('custom_admin:user_list')


@login_required
@admin_required
def donation_list(request):
    """Manage Donations."""
    donations = Donation.objects.all().order_by('-date_donated')
    return render(request, 'custom_admin/donation_list.html', {'donations': donations})


@login_required
@admin_required
def refund_donation(request, donation_id):
    """Refund donation."""
    donation = get_object_or_404(Donation, id=donation_id)
    if request.method == 'POST':
        # Mark as refunded (simulated refund for now)
        donation.payment_status = 'refunded'
        donation.save()
        messages.success(request, f"Donation {donation.invoice_number} marked as refunded.")
    return redirect('custom_admin:donation_list')


@login_required
@admin_required
def allocate_donation(request, donation_id):
    """Allocate donation amounts to active drives."""
    donation = get_object_or_404(Donation, id=donation_id)
    active_drives = Drive.objects.filter(status='active')
    allocated_so_far = donation.allocations.aggregate(Sum('allocated_amount'))['allocated_amount__sum'] or 0
    pending_allocation = donation.amount - allocated_so_far

    if request.method == 'POST':
        drive_id = request.POST.get('drive_id')
        amount = float(request.POST.get('amount', 0))

        if amount <= 0 or amount > float(pending_allocation):
            messages.error(request, f"Invalid amount. Must be between ₹0.01 and ₹{pending_allocation}")
        else:
            drive = get_object_or_404(Drive, id=drive_id)
            DonationAllocation.objects.create(
                donation=donation,
                drive=drive,
                allocated_amount=amount,
                used_amount=0,
                allocated_by=request.user
            )
            drive.budget_allocated += decimal_to_decimal(amount)
            drive.save()
            messages.success(request, f"Successfully allocated ₹{amount} to {drive.title}.")
            return redirect('custom_admin:donation_list')

    return render(request, 'custom_admin/allocate_donation.html', {
        'donation': donation,
        'active_drives': active_drives,
        'pending_allocation': pending_allocation,
    })


@login_required
@admin_required
def drive_list(request):
    """Manage Drives."""
    drives = Drive.objects.all().order_by('-created_at')
    return render(request, 'custom_admin/drive_list.html', {'drives': drives})


@login_required
@admin_required
def drive_form(request, drive_id=None):
    """Create or update a drive."""
    drive = None
    if drive_id:
        drive = get_object_or_404(Drive, id=drive_id)
        
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        city = request.POST.get('location_city')
        start_date_str = request.POST.get('start_date')
        status = request.POST.get('status', 'planning')
        budget = request.POST.get('budget_allocated', 0)
        
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        
        if drive:
            drive.title = title
            drive.description = description
            drive.location_city = city
            drive.start_date = start_date
            drive.status = status
            drive.budget_allocated = decimal_to_decimal(budget)
            if 'cover_image' in request.FILES:
                drive.cover_image = request.FILES['cover_image']
            drive.save()
            messages.success(request, "Drive updated successfully.")
        else:
            drive = Drive.objects.create(
                title=title,
                description=description,
                location_city=city,
                start_date=start_date,
                status=status,
                budget_allocated=decimal_to_decimal(budget),
                created_by=request.user,
                cover_image=request.FILES.get('cover_image')
            )
            messages.success(request, "Drive created successfully.")
        return redirect('custom_admin:drive_list')
        
    return render(request, 'custom_admin/drive_form.html', {'drive': drive})


@login_required
@admin_required
def notification_send(request):
    """Send announcements."""
    if request.method == 'POST':
        target_role = request.POST.get('target_role')
        title = request.POST.get('title')
        message = request.POST.get('message')

        if target_role == 'all':
            users = CustomUser.objects.all()
        else:
            users = CustomUser.objects.filter(role=target_role)
            
        for u in users:
            Notification.objects.create(
                recipient=u,
                title=title,
                message=message,
                notification_type='system'
            )
        messages.success(request, f"Announcement sent to {users.count()} users.")
        return redirect('custom_admin:dashboard')

    return render(request, 'custom_admin/notification_send.html')


@login_required
@admin_required
def settings_view(request):
    """Update organization settings."""
    settings = OrganizationSettings.get_settings()
    
    if request.method == 'POST':
        settings.name = request.POST.get('name')
        settings.contact_email = request.POST.get('contact_email')
        settings.contact_phone = request.POST.get('contact_phone')
        settings.address = request.POST.get('address')
        settings.tax_id = request.POST.get('tax_id')
        settings.legal_name = request.POST.get('legal_name')
        if 'logo' in request.FILES:
            settings.logo = request.FILES['logo']
        settings.save()
        messages.success(request, "Settings updated successfully.")
        return redirect('custom_admin:settings_view')
        
    return render(request, 'custom_admin/settings.html', {'settings': settings})


@login_required
@admin_required
def reports_view(request):
    """View and export reports."""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        
        response = HttpResponse(content_type='text/csv')
        
        if report_type == 'donations':
            response['Content-Disposition'] = f'attachment; filename="donations_{datetime.now().strftime("%Y%m%d")}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Invoice', 'Name', 'Email', 'Amount', 'Type', 'Status', 'Date'])
            for d in Donation.objects.all():
                writer.writerow([d.invoice_number, d.name, d.email, d.amount, d.donation_type, d.payment_status, d.date_donated.strftime("%Y-%m-%d")])
                
        elif report_type == 'users':
            response['Content-Disposition'] = f'attachment; filename="users_{datetime.now().strftime("%Y%m%d")}.csv"'
            writer = csv.writer(response)
            writer.writerow(['Name', 'Email', 'Role', 'Joined Date', 'Active'])
            for u in CustomUser.objects.all():
                writer.writerow([u.get_full_name(), u.email, u.role, u.date_joined.strftime("%Y-%m-%d"), str(u.is_active)])
                
        return response
        
    return render(request, 'custom_admin/reports.html')


def decimal_to_decimal(val):
    from decimal import Decimal
    return Decimal(str(val))
