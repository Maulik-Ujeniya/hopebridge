from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .models import CustomUser, UserPreference
from .forms import (
    RegistrationForm,
    ProfileEditForm,
    CustomPasswordChangeForm,
    OnboardingStep1Form,
    OnboardingStep2Form,
    OnboardingStep3Form,
    OnboardingStep4Form,
)


# ── Authentication Views ────────────────────────────────────────────

def get_dashboard_url(user):
    """Return the correct dashboard URL name based on user role."""
    if user.role == 'admin':
        return 'custom_admin:dashboard'
    elif user.role == 'volunteer':
        return 'volunteers:volunteer_dashboard'
    elif user.role == 'donor':
        return 'donations:donor_dashboard'
    else:
        return 'profile'

def login_view(request):
    """Login page with email + password."""
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))

    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.email}!')
            next_url = request.GET.get('next')
            if not next_url or next_url == '/':
                return redirect(get_dashboard_url(user))
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password. Please try again.')

    return render(request, 'accounts/login.html')


def register_view(request):
    """Registration page — Step 1 of signup."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            # Create empty preferences for onboarding
            UserPreference.objects.create(user=user)
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Account created successfully! Let\'s set up your preferences.')
            return redirect('onboarding_step1')
    else:
        form = RegistrationForm()
        next_url = request.GET.get('next')
        if next_url:
            request.session['onboarding_next_url'] = next_url

    return render(request, 'accounts/register.html', {'form': form})


def logout_view(request):
    """Log out and redirect to home."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


# ── Onboarding Views (4 Steps) ──────────────────────────────────────

@login_required
def onboarding_step1(request):
    """Step 1: What would you like to contribute?"""
    prefs, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = OnboardingStep1Form(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            return redirect('onboarding_step2')
    else:
        form = OnboardingStep1Form(instance=prefs)

    return render(request, 'accounts/onboarding/step1.html', {
        'form': form,
        'step': 1,
        'total_steps': 4,
    })


@login_required
def onboarding_step2(request):
    """Step 2: Role selection & experience."""
    prefs, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = OnboardingStep2Form(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            # Update user role based on preference
            role_map = {
                'donor': 'donor',
                'volunteer': 'volunteer',
                'coordinator': 'manager',
                'manager': 'manager',
            }
            preferred = form.cleaned_data.get('preferred_role', '')
            if preferred in role_map:
                request.user.role = role_map[preferred]
                request.user.save(update_fields=['role'])
            return redirect('onboarding_step3')
    else:
        form = OnboardingStep2Form(instance=prefs)

    return render(request, 'accounts/onboarding/step2.html', {
        'form': form,
        'step': 2,
        'total_steps': 4,
    })


@login_required
def onboarding_step3(request):
    """Step 3: Skills, availability & preferred categories."""
    prefs, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = OnboardingStep3Form(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            return redirect('onboarding_step4')
    else:
        form = OnboardingStep3Form(instance=prefs)

    return render(request, 'accounts/onboarding/step3.html', {
        'form': form,
        'step': 3,
        'total_steps': 4,
    })


@login_required
def onboarding_step4(request):
    """Step 4: Goals, motivation & submit."""
    prefs, _ = UserPreference.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = OnboardingStep4Form(request.POST, instance=prefs)
        if form.is_valid():
            form.save()
            request.user.is_profile_complete = True
            request.user.save(update_fields=['is_profile_complete'])
            
            # Automatically create sub-profiles if needed
            if request.user.role == 'volunteer':
                from volunteers.models import VolunteerProfile
                VolunteerProfile.objects.get_or_create(user=request.user)
                
            messages.success(request, '🎉 Profile setup complete! Welcome to HopeBridge!')
            
            # If they had an explicit destination (e.g. donate), go there.
            # Otherwise, go to onboarding success page.
            next_url = request.session.pop('onboarding_next_url', None)
            if next_url:
                return redirect(next_url)
            return redirect('onboarding_success')
    else:
        form = OnboardingStep4Form(instance=prefs)

    return render(request, 'accounts/onboarding/step4.html', {
        'form': form,
        'step': 4,
        'total_steps': 4,
    })


@login_required
def onboarding_success(request):
    """Success page shown after onboarding completion."""
    dashboard_url_name = get_dashboard_url(request.user)
    return render(request, 'accounts/onboarding_success.html', {
        'dashboard_url_name': dashboard_url_name
    })


# ── Profile Views ───────────────────────────────────────────────────

@login_required
def profile_view(request):
    """Display user profile with all data."""
    prefs, created = UserPreference.objects.get_or_create(user=request.user)
    
    # Impact Stats
    from donations.models import Donation
    from volunteers.models import VolunteerProfile
    from drives.models import DriveVolunteer
    from django.db.models import Sum
    
    total_donated = Donation.objects.filter(
        donor=request.user, payment_status='completed'
    ).aggregate(Sum('amount'))['amount__sum'] or 0
    
    try:
        vol_prof, created = VolunteerProfile.objects.get_or_create(user=request.user)
        total_hours = vol_prof.total_hours_worked
    except Exception:
        total_hours = 0
        
    recent_donations = Donation.objects.filter(
        donor=request.user, payment_status='completed'
    ).order_by('-date_donated')[:3]
    
    recent_drives = DriveVolunteer.objects.filter(
        volunteer=request.user
    ).select_related('drive').order_by('-joined_date')[:3]

    # Calculate Profile Completion
    fields_to_check = [
        request.user.first_name, request.user.phone, request.user.city, request.user.profile_picture,
        prefs.skills, prefs.motivation, prefs.experience_level, (prefs.wants_to_donate or prefs.wants_to_volunteer)
    ]
    completed_fields = sum(1 for field in fields_to_check if field)
    completion_percentage = int((completed_fields / len(fields_to_check)) * 100)

    # Profile calculations
    donations_qs = Donation.objects.filter(donor=request.user, payment_status='completed')
    
    # Calculate favorite category
    favorite_category = None
    if donations_qs.exists():
        from django.db.models import Count
        fav = donations_qs.values('donation_type').annotate(count=Count('donation_type')).order_by('-count').first()
        if fav:
            # map to readable string
            favorite_category = dict(Donation.DONATION_TYPE_CHOICES).get(fav['donation_type'], fav['donation_type'])
    
    average_donation = 0
    if total_donated > 0 and donations_qs.count() > 0:
        average_donation = total_donated / donations_qs.count()
        
    annual_contribution = total_donated # simplified calculation
    monthly_contribution = total_donated / 12 if total_donated > 0 else 0

    return render(request, 'accounts/profile.html', {
        'profile_user': request.user,
        'preferences': prefs,
        'total_donated': total_donated,
        'total_hours': total_hours,
        'recent_donations': recent_donations,
        'recent_drives': recent_drives,
        'completion_percentage': completion_percentage,
        'favorite_category': favorite_category,
        'average_donation': int(average_donation),
        'annual_contribution': annual_contribution,
        'monthly_contribution': int(monthly_contribution)
    })


@login_required
def profile_edit_view(request):
    """Edit user profile and preferences."""
    prefs, created = UserPreference.objects.get_or_create(user=request.user)
    
    # We must import the UserPreferenceEditForm
    from .forms import ProfileEditForm, UserPreferenceEditForm
    
    if request.method == 'POST':
        user_form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        pref_form = UserPreferenceEditForm(request.POST, instance=prefs)
        
        if user_form.is_valid() and pref_form.is_valid():
            user_form.save()
            pref_form.save()
            
            # Check if profile is effectively complete
            if not request.user.is_profile_complete and request.user.first_name and request.user.phone and request.user.city:
                request.user.is_profile_complete = True
                request.user.save()
                
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        user_form = ProfileEditForm(instance=request.user)
        pref_form = UserPreferenceEditForm(instance=prefs)

    return render(request, 'accounts/profile_edit.html', {
        'user_form': user_form,
        'pref_form': pref_form
    })


@login_required
def change_password_view(request):
    """Change password."""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully!')
            return redirect('profile')
    else:
        form = CustomPasswordChangeForm(request.user)

    return render(request, 'accounts/change_password.html', {'form': form})
